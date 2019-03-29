import asyncio
import json
import os
from typing import Tuple

from motor import MotorClient
from tornado.ioloop import IOLoop
from tornado.testing import AsyncHTTPTestCase
from app.urls import application
from app.models import User, Game
from main import ensure_ai_user


class BaseTest(AsyncHTTPTestCase):
    @classmethod
    def setUpClass(cls):
        cls.my_app = application

    def get_new_ioloop(self):
        return IOLoop.current()

    def get_app(self):
        return self.my_app


class TestRootApplication(BaseTest):

    def test_homepage(self,):
        response = self.fetch('/')
        self.assertEqual(response.code, 200)


class TestUserHandler(BaseTest):
    def get_app(self):
        db = MotorClient(
            os.getenv('DB_HOST', 'mongodb://localhost:27017'),
        )
        loop = asyncio.get_event_loop()
        loop.run_until_complete(db.drop_database(os.getenv('DB_NAME')))
        return application

    def create_user(self) -> str:
        user = User(username='usertest', email='test@test.de')
        loop = asyncio.get_event_loop()
        loop.run_until_complete(user.commit())
        return user.pk.__str__()

    def test_post_empty_json(self):
        response = self.fetch(
            '/api/users',
            method="POST",
            body="",
        )
        self.assertEqual(response.code, 400)

    def test_invalid_post(self):
        with open('app/tests/resources/user_invalid.json') as json:
            body = json.read()
        response = self.fetch(
            '/api/users',
            method="POST",
            body=body,
        )
        self.assertEqual(response.code, 500)

    def test_user_success(self):
        with open('app/tests/resources/user_success.json') as json:
            body = json.read()
        response = self.fetch(
            '/api/users',
            method="POST",
            body=body,
        )
        self.assertEqual(response.code, 200)

    def test_user_duplicated(self):
        self.create_user()
        with open('app/tests/resources/user_success.json') as json:
            body = json.read()
        response = self.fetch(
            '/api/users',
            method="POST",
            body=body,
        )
        self.assertEqual(response.code, 500)

    def test_get_user(self):
        user_id = self.create_user()
        response = self.fetch(
            '/api/users/%s' % user_id,
            method="GET",
        )
        self.assertEqual(response.code, 200)

    def test_get_user_invalid_mongo_id(self):
        response = self.fetch(
            '/api/users/%s' % '123456',
            method="GET",
        )
        self.assertEqual(response.code, 400)

    def test_get_user_not_found(self):
        mongo_id = '5c9d2b09e3872b287363cf28'
        response = self.fetch(
            '/api/users/%s' % mongo_id,
            method="GET",
        )
        self.assertEqual(response.code, 404)

    def test_update_user_not_found(self):
        with open('app/tests/resources/user_update.json') as json:
            body = json.read()
        user_id = '5c9d2b09e3872b287363cf28'
        response = self.fetch(
            '/api/users/%s' % user_id,
            method="PUT",
            body=body,
        )
        self.assertEqual(response.code, 404)

    def test_update_user_invalid_body(self):
        with open('app/tests/resources/user_update_invalid.json') as json:
            body = json.read()
        user_id = self.create_user()
        response = self.fetch(
            '/api/users/%s' % user_id,
            method="PUT",
            body=body,
        )
        self.assertEqual(response.code, 500)

    def test_update_user(self):
        with open('app/tests/resources/user_update.json') as json:
            body = json.read()
        user_id = self.create_user()
        response = self.fetch(
            '/api/users/%s' % user_id,
            method="PUT",
            body=body,
        )
        self.assertEqual(response.code, 200)

    def test_delete_user(self):
        user_id = self.create_user()
        response = self.fetch(
            '/api/users/%s' % user_id,
            method="DELETE",
        )
        self.assertEqual(response.code, 200)

    def test_delete_not_found(self):
        user_id = '5c9d2b09e3872b287363cf28'
        response = self.fetch(
            '/api/users/%s' % user_id,
            method="DELETE",
        )
        self.assertEqual(response.code, 404)

    def test_delete_success(self):
        user_id = self.create_user()
        response = self.fetch(
            '/api/users/%s' % user_id,
            method="DELETE",
        )
        self.assertEqual(response.code, 200)


class TestGameHandler(BaseTest):
    def get_app(self):
        db = MotorClient(
            os.getenv('DB_HOST', 'mongodb://localhost:27017'),
        )
        loop = asyncio.get_event_loop()
        loop.run_until_complete(db.drop_database(os.getenv('DB_NAME')))
        return application

    def create_player_one(self) -> str:
        user = User(username='playerone', email='player@one.te')
        loop = asyncio.get_event_loop()
        loop.run_until_complete(user.commit())
        return user.pk.__str__()

    def create_player_two(self) -> str:
        user = User(username='playertwo', email='player@two.te')
        loop = asyncio.get_event_loop()
        loop.run_until_complete(user.commit())
        return user.pk.__str__()

    def create_game(self) -> str:
        player_one_id = self.create_player_one()
        player_two_id = self.create_player_two()
        data = {"players": [player_one_id, player_two_id]}
        game = Game(**data)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(game.commit())
        return game.pk.__str__()

    def test_post_empty_json(self):
        response = self.fetch(
            '/api/games',
            method="POST",
            body="",
        )
        self.assertEqual(response.code, 400)

    def test_invalid_post(self):
        with open('app/tests/resources/game_invalid.json') as json:
            body = json.read()
        response = self.fetch(
            '/api/games',
            method="POST",
            body=body,
        )
        self.assertEqual(response.code, 500)

    def test_game_success_multiplayer(self):
        player_one_id = self.create_player_one()
        player_two_id = self.create_player_two()
        data = {"players": [player_one_id, player_two_id]}
        response = self.fetch(
            '/api/games',
            method="POST",
            body=json.dumps(data, ensure_ascii=False),
        )
        self.assertEqual(response.code, 200)

    def test_game_success_single_player(self):
        player_one_id = self.create_player_one()
        data = {"players": [player_one_id]}
        response = self.fetch(
            '/api/games',
            method="POST",
            body=json.dumps(data, ensure_ascii=False),
        )
        self.assertEqual(response.code, 200)

    def test_get_game(self):
        game_id = self.create_game()
        response = self.fetch(
            '/api/games/%s' % game_id,
            method="GET",
        )
        self.assertEqual(response.code, 200)

    def test_get_game_invalid_mongo_id(self):
        response = self.fetch(
            '/api/games/%s' % '123456',
            method="GET",
        )
        self.assertEqual(response.code, 400)

    def test_get_game_not_found(self):
        game_id = '5c9d2b09e3872b287363cf28'
        response = self.fetch(
            '/api/games/%s' % game_id,
            method="GET",
        )
        self.assertEqual(response.code, 404)


class TestPlay(BaseTest):
    def get_app(self):
        db = MotorClient(
            os.getenv('DB_HOST', 'mongodb://localhost:27017'),
        )
        loop = asyncio.get_event_loop()
        loop.run_until_complete(db.drop_database(os.getenv('DB_NAME')))
        return application

    def create_player_one(self) -> str:
        user = User(username='playerone', email='player@one.te')
        loop = asyncio.get_event_loop()
        loop.run_until_complete(user.commit())
        return user.pk.__str__()

    def create_player_two(self) -> str:
        user = User(username='playertwo', email='player@two.te')
        loop = asyncio.get_event_loop()
        loop.run_until_complete(user.commit())
        return user.pk.__str__()

    def create_player_three(self) -> str:
        user = User(username='playerthree', email='player@three.te')
        loop = asyncio.get_event_loop()
        loop.run_until_complete(user.commit())
        return user.pk.__str__()

    def create_game(self) -> Tuple:
        player_one_id = self.create_player_one()
        player_two_id = self.create_player_two()
        data = {"players": [player_one_id, player_two_id]}
        game = Game(**data)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(game.commit())
        return game.pk.__str__(), player_one_id, player_two_id

    def create_single_player_game(self) -> Tuple:
        ensure_ai_user()
        player_one_id = self.create_player_one()
        data = {"players": [player_one_id]}
        game = Game(**data)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(game.commit())
        return game.pk.__str__(), player_one_id

    def test_game_move_invalid_move(self):
        game_id, player_one, player_two = self.create_game()
        data = {
            "player": player_one,
            "symbol": "X",
            "cell": {
                "row": 3,
                "column": 3
            }
        }
        response = self.fetch(
            '/api/games/%s' % game_id,
            method="POST",
            body=json.dumps(data, ensure_ascii=False),
        )
        self.assertEqual(response.code, 412)

    def test_valid_move(self):
        game_id, player_one, player_two = self.create_game()
        data = {
            "player": player_one,
            "symbol": "X",
            "cell": {
                "row": 0,
                "column": 0
            }
        }
        response = self.fetch(
            '/api/games/%s' % game_id,
            method="POST",
            body=json.dumps(data, ensure_ascii=False),
        )
        self.assertEqual(response.code, 200)

    def test_same_user_move(self):
        game_id, player_one, player_two = self.create_game()
        data = {
            "player": player_one,
            "symbol": "X",
            "cell": {
                "row": 0,
                "column": 0
            }
        }
        self.fetch(
            '/api/games/%s' % game_id,
            method="POST",
            body=json.dumps(data, ensure_ascii=False),
        )
        data = {
            "player": player_one,
            "symbol": "X",
            "cell": {
                "row": 0,
                "column": 0
            }
        }
        response = self.fetch(
            '/api/games/%s' % game_id,
            method="POST",
            body=json.dumps(data, ensure_ascii=False),
        )
        self.assertEqual(response.code, 412)

    def test_same_symbol(self):
        game_id, player_one, player_two = self.create_game()
        data = {
            "player": player_one,
            "symbol": "X",
            "cell": {
                "row": 0,
                "column": 0
            }
        }
        self.fetch(
            '/api/games/%s' % game_id,
            method="POST",
            body=json.dumps(data, ensure_ascii=False),
        )
        data = {
            "player": player_two,
            "symbol": "X",
            "cell": {
                "row": 0,
                "column": 0
            }
        }
        response = self.fetch(
            '/api/games/%s' % game_id,
            method="POST",
            body=json.dumps(data, ensure_ascii=False),
        )
        self.assertEqual(response.code, 412)

    def test_same_cell(self):
        game_id, player_one, player_two = self.create_game()
        data = {
            "player": player_one,
            "symbol": "X",
            "cell": {
                "row": 0,
                "column": 0
            }
        }
        self.fetch(
            '/api/games/%s' % game_id,
            method="POST",
            body=json.dumps(data, ensure_ascii=False),
        )
        data = {
            "player": player_two,
            "symbol": "O",
            "cell": {
                "row": 0,
                "column": 0
            }
        }
        response = self.fetch(
            '/api/games/%s' % game_id,
            method="POST",
            body=json.dumps(data, ensure_ascii=False),
        )
        self.assertEqual(response.code, 412)

    def test_second_move(self):
        game_id, player_one, player_two = self.create_game()
        data = {
            "player": player_one,
            "symbol": "X",
            "cell": {
                "row": 0,
                "column": 0
            }
        }
        self.fetch(
            '/api/games/%s' % game_id,
            method="POST",
            body=json.dumps(data, ensure_ascii=False),
        )
        data = {
            "player": player_two,
            "symbol": "O",
            "cell": {
                "row": 1,
                "column": 1
            }
        }
        response = self.fetch(
            '/api/games/%s' % game_id,
            method="POST",
            body=json.dumps(data, ensure_ascii=False),
        )
        self.assertEqual(response.code, 200)

    def test_single_player(self):
        game_id, player_one = self.create_single_player_game()
        data = {
            "player": player_one,
            "symbol": "X",
            "cell": {
                "row": 0,
                "column": 0
            }
        }
        response = self.fetch(
            '/api/games/%s' % game_id,
            method="POST",
            body=json.dumps(data, ensure_ascii=False),
        )
        print(response.body.decode())
        self.assertEqual(response.code, 200)

"""
Collection of project handlers
"""
import json
from tornado.web import RequestHandler, HTTPError
from tornado.escape import json_decode
from umongo import fields

from app.decorators import validate_mongo_id, validate_json_body
from app.models import Game, GameMove
from app.engine import GameEngine


engine = GameEngine()


class MainHandler(RequestHandler):
    """
    Main handler to return the default responses
    """
    async def get(self):
        """
        Base handler, hello world
        :return:
        """
        self.set_header("Content-Type", 'application/json')
        self.write({"Hello": "World"})


class ErrorHandler(RequestHandler):
    """
    This class allows us to handle the HTTPErrors and exceptions
    """
    def write_error(self, status_code, **kwargs):
        """
        This method takes the HTTPError and renders a json
        based on it
        :param status_code:
        :param kwargs:
        :return:
        """
        self.set_header('Content-Type', 'application/json')
        status_code = 500
        if "exc_info" in kwargs:
            exception = kwargs.get('exc_info')[1]
            self._reason = exception.__str__()
            status_code = getattr(exception, 'status_code', 400)
        self.finish(json.dumps({
            'error': {
                'code': status_code,
                'message': self._reason,
            }
        }))


class AbstractGeneralHandler(ErrorHandler):
    """
    General operations that require no objectId,
    This includes POST and GET list operations.
    """
    def initialize(self, cls):
        """
        Initialize the class variable with ODM definition
        :param cls: umongo ODM class definition
        :return:
        """
        self.cls = cls

    @validate_json_body
    async def post(self):
        """
        Create a new object by the POST json body
        :return:
        """
        data = json_decode(self.request.body)
        obj = self.cls(**data)
        await obj.ensure_indexes()
        await obj.commit()
        self.set_header("Content-Type", 'application/json')
        self.write(obj.dump())

    async def get(self):
        """
        Retrieve a list of objects
        :return:
        """
        cursor = self.cls.find()
        data = []
        async for obj in cursor:
            data.append(obj.dump())
        self.set_header("Content-Type", 'application/json')
        self.write({'data': data})


class AbstractObjHandler(ErrorHandler):
    """
    This handler has the methods to manipulate a single object
    based on its ObjectId
    """
    def initialize(self, cls):
        """
        Initialize the class variable with ODM definition
        :param cls: umongo ODM class definition
        :return:
        """
        self.cls = cls

    @validate_mongo_id
    async def get(self, pk: str):
        """
        Retrieve a single object from the database
        :param str pk:
        :return:
        """
        obj = await self.cls.find_by_id(pk)
        self.set_header("Content-Type", 'application/json')
        self.write(obj.dump())

    @validate_mongo_id
    @validate_json_body
    async def put(self, pk: str):
        """
        Edit a given database object
        :param str pk:
        :return:
        """
        obj = await self.cls.find_by_id(pk)
        data = json_decode(self.request.body)
        obj.update(data)
        await obj.commit()
        self.set_header("Content-Type", 'application/json')
        self.write(obj.dump())

    @validate_mongo_id
    async def delete(self, pk: str):
        """
        Remove a given database object
        :param str pk:
        :return:
        """
        obj = await self.cls.find_by_id(pk)
        await obj.delete()
        self.set_header("Content-Type", 'application/json')
        self.write({'success': True})


class GameMoveHandler(ErrorHandler):
    """
    This class allows us to trigger execute board move
    operations
    """

    @validate_mongo_id
    @validate_json_body
    async def post(self, pk: str):
        """
        Edit a given database object
        :param str pk:
        :return:
        """
        game: Game = await Game.find_by_id(pk)
        if game.status in [Game.STATUS_TIE, Game.STATUS_FINISHED]:
            raise HTTPError(
                400,
                'Game was already finished'
            )
        data = json_decode(self.request.body)
        move = GameMove(**data)
        await engine.execute_move(game, move)
        if not game.multiplayer and game.status == Game.STATUS_IN_PROGRESS:
            aimove = await engine.ai_move(game, move)
            await engine.execute_move(game, aimove)
        self.set_header("Content-Type", 'application/json')
        self.write(game.dump())

    @validate_mongo_id
    async def get(self, pk: str):
        """
        Retrieve a single object from the database
        :param str pk:
        :return:
        """
        obj = await Game.find_by_id(pk)
        self.set_header("Content-Type", 'application/json')
        self.write(obj.dump())


class GameMovesRetriever(ErrorHandler):
    """
    This handler allows us to retrieve the moves trace for a
    given game.
    """
    @validate_mongo_id
    async def get(self, pk: str):
        """
        Retrieve a list of moves from the database
        :param str pk:
        :return:
        """

        cursor = GameMove.find({"game": fields.ObjectId(pk)})
        data = []
        async for obj in cursor:
            data.append(obj.dump())
        self.set_header("Content-Type", 'application/json')
        self.write({"data": data})


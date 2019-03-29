"""
Launcher of the application
"""
import os
import asyncio
from tornado import ioloop
from app.urls import application
from app.models import User, Game, GameMove


def ensure_ai_user():
    """
    AI User creation
    :return:
    """
    data = {'username': 'tictactoeai', 'email': 'ai@robot.de'}
    loop = asyncio.get_event_loop()
    ai = loop.run_until_complete(User.find_one({'username': 'tictactoeai'}))
    if ai:
        return
    ai = User(**data)
    loop.run_until_complete(ai.commit())
    pass


def main():
    """
    Main launcher of the webApp
    :return:
    """
    app = application
    ensure_ai_user()
    app.listen(os.getenv('PORT', "8000"))
    ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()

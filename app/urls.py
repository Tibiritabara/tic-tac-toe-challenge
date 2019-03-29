"""
Collection of project routes and where do they point to
"""
import os
from tornado.web import Application, url
from app.models import User, Game, GameMove
import app.handlers


application = Application([
        url(
            r"/",
            app.handlers.MainHandler,
        ),
        url(
            r"/api/users",
            app.handlers.AbstractGeneralHandler,
            {'cls': User},
        ),
        url(
            r"/api/users/(?P<pk>\w+)",
            app.handlers.AbstractObjHandler,
            {'cls': User},
        ),
        url(
            r"/api/games",
            app.handlers.AbstractGeneralHandler,
            {'cls': Game}
        ),
        url(
            r"/api/games/(?P<pk>\w+)",
            app.handlers.GameMoveHandler,
        ),
        url(
            r"/api/games/(?P<pk>\w+)/moves",
            app.handlers.GameMovesRetriever,
        ),
    ],
    debug=os.getenv('DEBUG_FLAG') == "True",
)

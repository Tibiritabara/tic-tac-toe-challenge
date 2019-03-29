"""
Module with the object definitions that are going to be stored
"""
import os
import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from tornado.web import HTTPError
from umongo import Instance, \
    Document, \
    fields, \
    validate, \
    ValidationError


db = AsyncIOMotorClient(
    os.getenv('DB_HOST', 'mongodb://localhost:27017'),
)[os.getenv('DB_NAME', 'tictactoe')]
instance = Instance(db)


@instance.register
class BaseDocument(Document):
    """
    This class looks to implement a common method on all of our
    produced documents.
    """

    @classmethod
    async def find_by_id(cls, pk: str):
        """
        Abstraction to throw an exception in case an object
        does not exist on db.
        :param str pk:
        :return:
        """
        obj = await cls.find_one(
            {"_id": fields.ObjectId(pk)}
        )
        if obj is None:
            raise HTTPError(
                404,
                'Object not found Not Found',
            )
        return obj

    class Meta:
        """
        ODM Metadata
        """
        allow_inheritance = True
        abstract = True


@instance.register
class User(BaseDocument):
    """
    This document stores the user information and data
    as the number of victories and defeats
    """
    username = fields.StrField(
        required=True,
        unique=True,
        validate=[validate.Length(min=6, max=20)],
    )

    email = fields.StrField(
        required=True,
        unique=True,
        validate=validate.Email(),
    )

    victories = fields.IntField(
        default=0,
    )

    created_at = fields.DateTimeField(
        default=datetime.datetime.now(),
    )

    class Meta:
        """
        ODM Metadata
        """
        collection = db.users


@instance.register
class Game(BaseDocument):
    """
    This is how we are going to store the game
    """
    STATUS_CREATED = 'created'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_TIE = 'tie'
    STATUS_FINISHED = 'finished'

    STATUS = [
        STATUS_CREATED,
        STATUS_IN_PROGRESS,
        STATUS_TIE,
        STATUS_FINISHED,
    ]

    players = fields.ListField(
        fields.ReferenceField("User"),
    )

    multiplayer = fields.BoolField(
        default=False,
    )

    board = fields.ListField(
        fields.ListField(
            fields.StrField()
        )
    )

    status = fields.StrField(
        validate=validate.OneOf(STATUS),
        default=STATUS_CREATED
    )

    created_at = fields.DateTimeField(
        default=datetime.datetime.now(),
    )

    winner = fields.ReferenceField("User")

    def pre_insert(self):
        """
        Fill the board and do multiplayer validations
        """
        if not self.players:
            raise ValidationError(
                "There should be at least one player",
            )
        if len(self.players) > 2:
            raise ValidationError(
                "Maximum two players"
            )
        if len(self.players) == 2:
            self.multiplayer = True
        else:
            self.multiplayer = False

        self.board = [['', '', ''], ['', '', ''], ['', '', '']]
        pass

    class Meta:
        """
        ODM Metadata
        """
        collection = db.games


@instance.register
class GameMove(BaseDocument):
    """
    This collection will track the moves of the users
    on the given game
    """

    SYMBOLS = [
        'X',
        'O'
    ]

    game = fields.ReferenceField(
        "Game",
    )

    cell = fields.DictField(
        required=True
    )

    symbol = fields.StrField(
        validate=validate.OneOf(SYMBOLS),
        required=True,
    )

    player = fields.ReferenceField(
        "User",
        required=True,
    )

    created_at = fields.DateTimeField(
        default=datetime.datetime.now(),
    )

    class Meta:
        """
        ODM Metadata
        """
        collection = db.moves

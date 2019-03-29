"""
Set of decorators useful for the main tool handlers
"""
import bson
from tornado.web import HTTPError


def validate_mongo_id(func):
    """
    Validate that the input contains a valid mongoId
    :param func:
    :return:
    """
    def wrapper(*args, **kwargs):
        if not bson.objectid.ObjectId.is_valid(kwargs.get('pk', None)):
            raise HTTPError(400, 'Invalid Mongo Id')
        return func(*args, **kwargs)
    return wrapper


def validate_json_body(func):
    """
    Validate that the body of the request is not empty
    If is empty throw a 400 exception
    :param func:
    :return:
    """
    def wrapper(*args, **kwargs):
        if not args[0].request.body:
            raise HTTPError(400, 'Empty request body')
        return func(*args, **kwargs)
    return wrapper

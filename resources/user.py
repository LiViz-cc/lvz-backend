import datetime

from errors import ForbiddenError, InvalidParamError, NotFinishedYet, NotFoundError
from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from models import User
from mongoengine.errors import DoesNotExist, ValidationError
from services import UserService

from utils.guard import myguard
from utils.logger import get_the_logger
from .response_wrapper import response_wrapper

logger = get_the_logger()


class UserResource(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.user_service = UserService()

    @response_wrapper
    @jwt_required()
    def get(self, id):
        # check authorization
        jwt_id = get_jwt_identity()
        logger.info('GET user by id {} with jwt_id {}'.format(id, jwt_id))
        return self.user_service.get_user_by_id(id, jwt_id)


class UserPasswordResource(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.user_service = UserService()

    @response_wrapper
    @jwt_required()
    def post(self, id):
        # get request args
        args = request.args

        # get request body dict
        body = request.get_json()

        # check authorization
        jwt_id = get_jwt_identity()

        # query project via id
        old_password = args.get('password', None)
        new_password = body.get('password', None)

        return self.user_service.change_password(id, jwt_id, old_password, new_password)

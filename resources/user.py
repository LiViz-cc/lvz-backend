
from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from errors import ForbiddenError, InvalidParamError
from services import UserService
import utils
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
        # get request body dict
        body = request.get_json()

        # check authorization
        jwt_id = get_jwt_identity()

        # query project via id
        old_password = body.get('old_password', None)
        new_password = body.get('new_password', None)

        # check params
        utils.myguard.check_literaly.check_type([
            (str, old_password, 'old_password', False),
            (str, new_password, 'new_password', False)
        ])

        return self.user_service.change_password(id, jwt_id, old_password, new_password)


class UserResetResource(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.user_service = UserService()

    @response_wrapper
    @jwt_required()
    def post(self, id):
        # NOTE: Danger! This method is only allowed in development mode

        # check if in development mode
        import os
        env = os.getenv('ENV')
        if env != 'development':
            raise ForbiddenError(
                'Resetting a user is only allowed in development')

        body = request.get_json()
        password = body.get('password')
        # check authorization
        jwt_id = get_jwt_identity()

        return self.user_service.reset_by_id(id, password, jwt_id)


class UserUsernameResource(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.user_service = UserService()

    @response_wrapper
    @jwt_required()
    def post(self, id):
        body = request.get_json()
        user_id = id
        username, password = [body.get(x) for x in ['username', 'password']]
        jwt_id = get_jwt_identity()

        utils.myguard.check_literaly.check_type([
            (str, user_id, 'user_id', False),
            (str, username, 'username', False),
            (str, password, 'password', False),
        ])

        return self.user_service.change_username(
            user_id=user_id,
            username=username,
            password=password,
            jwt_id=jwt_id,
        )

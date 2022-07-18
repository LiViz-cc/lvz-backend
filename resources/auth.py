
import email

import utils
from errors import InvalidParamError
from flask import request
from flask_restful import Resource
from services import (DataSourcesService, DisplaySchemaService, ProjectService,
                      ShareConfigService, UserService)
from utils.logger import get_the_logger

from .response_wrapper import response_wrapper

logger = get_the_logger()


class SignupResource(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.user_service = UserService()

    @response_wrapper
    def post(self):
        # get request body dict
        body = request.get_json()

        # Unpack body
        email = body.get('email', None)
        password = body.get('password', None)
        username = body.get('username')

        # check literally
        utils.myguard.check_literaly.check_type([
            (str, email, 'email', False),
            (str, password, 'password', False),
            (str, username, 'username', True)
        ])
        utils.myguard.check_literaly.password(
            password=password,
            is_new=True,
            password_alies='password'
        )

        return self.user_service.signUp(email, password, username)


class LoginResource(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.user_service = UserService()

    @response_wrapper
    def post(self):
        # get request body dict
        body = request.get_json()

        logger.info('Try to log in. Message body: {}'.format(body))
        email = body.get('email', None)
        password = body.get('password', None)
        username = body.get('username')

        if email is None and username is None:
            raise InvalidParamError('Please provide email or username.')

        if email is not None and username is not None:
            raise InvalidParamError('Please provide either username or email.')

        return self.user_service.login(email, password, username)

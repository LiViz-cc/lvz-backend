
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

        return self.user_service.signUp(body)


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

        return self.user_service.login(email, password)

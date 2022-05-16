from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token
import datetime
import json
from models import User
from mongoengine.errors import NotUniqueError, ValidationError, DoesNotExist
from errors import InvalidParamError, EmailAlreadyExistsError, UnauthorizedError
from .response_wrapper import response_wrapper


class SignupResource(Resource):
    @response_wrapper
    def post(self):
        # get request body dict
        body = request.get_json()

        # pre-validate params
        password = body.get('password', None)
        if type(password) != str:
            raise InvalidParamError('Password (string) must be provided.')
        if len(password) < 6 or len(password) > 20:
            raise InvalidParamError(
                'Password length must between 6 and 20 (included).')
        # TODO more rules, e.g. special character limit, complexity level, etc.

        # construct new user object
        user = User(**body)

        # set time
        curr_time = datetime.datetime.utcnow
        user.created = curr_time
        user.modified = curr_time

        # hash passord
        user.hash_password()  # must manually call this function before save

        # save new user
        try:
            user.save()
        except ValidationError as e:
            raise InvalidParamError(e.message)
        except NotUniqueError:
            raise EmailAlreadyExistsError(body['email'])

        # return desensitized created user
        user.desensitize()
        return user


class LoginResource(Resource):
    @response_wrapper
    def post(self):
        # get request body dict
        body = request.get_json()

        # pre-validate params
        email = body.get('email', None)
        if type(email) != str:
            raise InvalidParamError('Email (string) must be provided.')
        password = body.get('password', None)
        if type(password) != str:
            raise InvalidParamError('Password (string) must be provided.')

        # query user
        try:
            user = User.objects.get(email=email)
        except DoesNotExist:
            raise UnauthorizedError()

        # check password
        if not user.check_password(password):
            raise UnauthorizedError()

        # create access token
        expires = datetime.timedelta(days=7)
        access_token = create_access_token(
            identity=str(user.id), expires_delta=expires)
        return {'token': access_token, 'user': json.loads(user.to_json())}

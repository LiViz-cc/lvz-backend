import datetime

from errors import ForbiddenError, InvalidParamError, NotFinishedYet, NotFoundError
from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from models import User
from mongoengine.errors import DoesNotExist, ValidationError

from utils.guard import myguard
from .response_wrapper import response_wrapper


class UserResource(Resource):
    @response_wrapper
    @jwt_required()
    def get(self, id):
        # query user via id
        try:
            user = User.objects.get(id=id)
        except DoesNotExist:
            raise NotFoundError('user', 'id={}'.format(id))

        # check authorization
        user_id = get_jwt_identity()
        myguard.check_literaly.user_id(user_id)

        # user can only get their own info
        if user_id != str(user.id):
            raise ForbiddenError()

        user.desensitize()
        return user


class UserPasswordResource(Resource):
    @response_wrapper
    @jwt_required()
    def post(self, id):
        # get request args
        args = request.args

        # get request body dict
        body = request.get_json()

        # query project via id
        myguard.check_literaly.object_id(id)

        # get user from database
        try:
            user = User.objects.get(id=id)
        except DoesNotExist:
            raise NotFoundError('user', 'id={}'.format(id))
        user: User

        # check authorization
        user_id = get_jwt_identity()
        myguard.check_literaly.user_id(user_id)
        if id != user_id:
            raise ForbiddenError()

        # check if old_password is as same as the password in the database
        old_password = args.get('password', None)
        myguard.check_literaly.password(old_password, is_new=False)
        if not user.check_password(old_password):
            raise ForbiddenError("Password is wrong.")

        # check if new_password valid
        new_password = body.get('password', None)
        myguard.check_literaly.password(new_password, is_new=True)

        # Forbid changing immutable field
        modifing_dict = {}
        # add password into dict
        modifing_dict['password'] = User.get_password_hash(new_password)
        modifing_dict['modified'] = datetime.datetime.utcnow

        # update project
        try:
            user.modify(**modifing_dict)
        except ValidationError as e:
            raise InvalidParamError(e.message)
        except LookupError as e:
            raise InvalidParamError(e.message)

        user.desensitize()
        return user

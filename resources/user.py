from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine.errors import DoesNotExist
from .response_wrapper import response_wrapper
from models import User
from mongoengine.errors import DoesNotExist
from errors import NotFoundError, ForbiddenError


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
        if user_id != str(user.id):
            raise ForbiddenError()

        user.desensitize()
        return user

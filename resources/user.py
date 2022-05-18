from errors import ForbiddenError, NotFoundError
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from models import User
from mongoengine.errors import DoesNotExist

from .guard import myguard
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
        myguard.check.user_id(user_id)

        # user can only get their own info
        if user_id != str(user.id):
            raise ForbiddenError()

        user.desensitize()
        return user

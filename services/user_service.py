import datetime
from dao.user_dao import UserDao

from errors import (ForbiddenError, InvalidParamError, NotFinishedYet,
                    NotFoundError)
from models import DataSource, Project, ShareConfig, User
from mongoengine.errors import DoesNotExist, ValidationError
from utils.guard import myguard


class UserService():
    def __init__(self) -> None:
        self.user_dao = UserDao()

    def get_user_by_id(self, id, jwt_id) -> User:
        # check authorization
        myguard.check_literaly.user_id(jwt_id)

        # query user via id
        try:
            user = User.objects.get(id=id)
        except DoesNotExist:
            raise NotFoundError('user', 'id={}'.format(id))

        # user can only get their own info
        if jwt_id != str(user.id):
            raise ForbiddenError()

        user.desensitize()
        return user

    def get_user_by_jwt_id(self, jwt_id) -> User:
        # check authorization
        myguard.check_literaly.user_id(jwt_id)

        # query user via id
        try:
            user = User.objects.get(id=jwt_id)
        except DoesNotExist:
            raise NotFoundError('user', 'id={}'.format(id))

        user.desensitize()
        return user

    def change_password(self, id, jwt_id, old_password, new_password):
        # get user from database
        myguard.check_literaly.object_id(id)
        try:
            user = User.objects.get(id=id)
        except DoesNotExist:
            raise NotFoundError('user', 'id={}'.format(id))
        user: User

        # check authorization
        myguard.check_literaly.user_id(jwt_id)
        if id != jwt_id:
            raise ForbiddenError()

        # check if old_password is as same as the password in the database
        myguard.check_literaly.password(old_password, is_new=False)
        if not user.check_password(old_password):
            raise ForbiddenError("Password is wrong.")

        # check if new_password valid
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

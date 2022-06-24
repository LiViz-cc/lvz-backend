
from errors import (ForbiddenError, InvalidParamError, NotFinishedYet,
                    NotFoundError)
from models import DataSource, Project, ShareConfig, User
from mongoengine.errors import DoesNotExist, ValidationError
from utils.guard import myguard
from utils.common import *


class UserDao:
    def get_user_by_id(self, id: str) -> User:
        # check authorization
        myguard.check_literaly.user_id(id)

        # query user via id
        try:
            user = User.objects.get(id=id)
        except DoesNotExist:
            raise NotFoundError('user', 'id={}'.format(id))

        user.desensitize()
        return user

    def save(self, user: User):
        try:
            user.save()
        except ValidationError as e:
            raise InvalidParamError(e.message)

    def add_project(self, user: User, project: Project) -> None:
        try:
            user.update(push__projects=project)
        except ValidationError as e:
            raise InvalidParamError(e.message)

    def add_data_source(self, user: User, data_source: DataSource):
        try:
            user.update(push__data_sources=data_source)
        except ValidationError as e:
            raise InvalidParamError(e.message)

    def hash_password(self, user: User):
        user.password = generate_password_hash(user.password).decode('utf8')

    def check_password(self, user: User, password):
        return check_password_hash(user.password, password)

    def desensitize(self, user: User):
        if hasattr(user, 'password'):
            del user.password

    def get_password_hash(self, password: str) -> str:
        """
        Please confirm the password is valid before calling this method

        Args:
            password (str): password

        Returns:
            hashed_password (str): hashed password
        """
        return generate_password_hash(password).decode('utf8')

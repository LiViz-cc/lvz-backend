
from errors import (ForbiddenError, InvalidParamError, NotFinishedYet,
                    NotFoundError)
from models import DataSource, Project, ShareConfig, User
from mongoengine.errors import DoesNotExist, ValidationError
from utils.guard import myguard
from utils.common import *


class UserDao:
    def save(self, user: User) -> None:
        try:
            user.save()
        except ValidationError as e:
            raise InvalidParamError(e.message)
        except NotUniqueError:
            raise EmailAlreadyExistsError(user.email)

    def modify(self, user: User, modifing_dict: dict) -> None:
        # update project
        try:
            user.modify(**modifing_dict)
        except ValidationError as e:
            raise InvalidParamError(e.message)
        except LookupError as e:
            raise InvalidParamError(e.message)

    def get_user_by_id_with_sensitive_info(self, id: str) -> User:
        # check authorization
        myguard.check_literaly.user_id(id)

        # query user via id
        try:
            user = User.objects.get(id=id)
        except DoesNotExist:
            raise NotFoundError('user', 'id={}'.format(id))

        return user

    def get_user_by_id(self, id: str) -> User:
        user = self.get_user_by_id_with_sensitive_info(id)

        user.desensitize()
        return user

    def get_user_by_email_with_sensitive_info(self, email: str) -> User:
        try:
            user = User.objects.get(email=email)
        except DoesNotExist:
            raise UnauthorizedError()
        return user

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
        if not hasattr(user, 'password'):
            raise InvalidParamError(
                'desentitized user has no password attributes')

        user.password = generate_password_hash(user.password).decode('utf8')

    def check_password(self, user: User, password):
        myguard.check_literaly.password(password, is_new=False)
        return check_password_hash(user.password, password)

    def assert_password_match(self, user: User, password):
        if not self.check_password(user, password):
            raise ForbiddenError("Password is wrong.")

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

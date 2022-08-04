

from errors import (EmailAlreadyExistsError, ForbiddenError, InvalidParamError,
                    NotFoundError, NotMutableError, UnauthorizedError)
from flask_bcrypt import check_password_hash, generate_password_hash
from models import DataSource, DisplaySchema, Project, ShareConfig, User
from mongoengine.errors import DoesNotExist, NotUniqueError, ValidationError
import utils
from utils.guard import myguard


class UserDao:
    def save(self, user: User, *args, **kwargs) -> None:
        try:
            user.save(*args, **kwargs)
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
        """
        Args:
            id (str): user_id

        Returns:
            User: desensitized user with provided id
        """
        user = self.get_user_by_id_with_sensitive_info(id)

        user.desensitize()
        return user

    def get_user_by_email_with_sensitive_info(self, email: str) -> User:
        try:
            user = User.objects.get(email=email)
        except DoesNotExist:
            raise UnauthorizedError()
        return user

    def get_user_by_username(self, username: str, desensitized=True) -> User:
        try:
            user = User.objects.get(username=username)
        except DoesNotExist:
            raise NotFoundError('user', 'username={}'.format(username))

        if desensitized:
            self.desensitize(user)
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
        if not user:
            raise InvalidParamError('User for hashing password cannot be null')
        if not hasattr(user, 'password'):
            raise InvalidParamError(
                'desentitized user has no password attributes')

        user.password = generate_password_hash(user.password).decode('utf8')

    def check_password(self, user: User, password):
        myguard.check_literaly.password(password, is_new=False)
        try:
            if user.password == None:
                raise InvalidParamError('desensitized user has no passwords')
        except DoesNotExist as e:
            raise InvalidParamError('desensitized user has no passwords')

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

    def delete(self, user: User, *args, **kwargs) -> None:
        myguard.check_literaly.check_type([
            (User, user, "User", False)
        ])

        try:
            user.delete(*args, **kwargs)
        except DoesNotExist as e:
            raise NotFoundError('User', 'id={}'.format(
                getattr(user, 'id', 'None')))

    def change_username(self, user: User, username: str) -> User:
        myguard.check_literaly.check_type([
            (User, user, "User", False)
        ])

        # update project
        try:
            user.modify(username=username)
        except ValidationError as e:
            raise InvalidParamError(e.message)
        except LookupError as e:
            raise InvalidParamError(e.message)
        except NotUniqueError as e:
            raise InvalidParamError(
                'Username {} is not unique.'.format(username))

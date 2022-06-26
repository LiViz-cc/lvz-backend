from typing import List, Tuple, Type
from errors import InvalidParamError, UnauthorizedError
from collections import namedtuple

Check_Tuple = namedtuple(
    'Check_Tuple', ['type', 'para', 'name', 'nullable'])


class CheckingCenter():
    """
    A class as a literal checker.
    Caution: Please note it will only check if the parameters are literaly correct.
    No guarantee whether the input is valid in the database or whether it is reachable.
    """

    def __init__(self) -> None:
        self.LENGTH_OF_DATA_OBJECT_ID = 24
        self.MIN_LENGTH_OF_PASSWORD = 6
        self.MAX_LENGTH_OF_PASSWORD = 20

    def user_id(self, user_id: str):
        """
        Check if `user_id` is valid
        Caution: Only check if `user_id` is literally a valid string.
        No guarantee whether `user_id` exists in the database or whether it is reachable.

        Args:
            user_id (str): user id

        Raises:
            UnauthorizedError: raises if `user_id` is null or not a string

        Returns:
            self: return itself for a stream operation
        """
        if user_id is None or type(user_id) != str:
            raise UnauthorizedError()
        return self

    def object_id(self, object_id: str, object_name="object"):
        """
        Check if `object_id` is valid
        Caution: Only check if the `object_id` is literally a valid string.
        No guarantee whether the id of object exists in the database or whether it is reachable.

        Args:
            id (str): id

        Raises:
            InvalidParamError: raises if `id` is null or not a string

        Returns:
            self: return itself for a stream operation
        """

        if object_id is None:
            raise InvalidParamError(
                "The {} with such id is not found.".format(object_name))

        if not isinstance(object_id, str):
            raise InvalidParamError(
                "The {} is not an instance of String.".format(object_name))

        if len(object_id) != self.LENGTH_OF_DATA_OBJECT_ID:
            raise InvalidParamError(
                "The id of {} must be a 24-character string.".format(object_name))

        return self

    def password(self, password: str, is_new: bool, password_alies='password'):
        """
        Check if `password` is valid
        Caution: Only check if the `password` is literally a valid string.
        No guarantee whether password is correct in the database.

        Args:
            password (str): password
            is_new (bool): True if it is a new user or a new password for an existed user

        Raises:
            InvalidParamError: raises if parameter types are not correct or password is too short or too long

        Returns:
            self: return itself for a stream operation
        """

        if type(is_new) != bool:
            raise InvalidParamError('"is_new" must be a boolean.')

        if password is None:
            raise InvalidParamError(
                '"{}" cannot be null.'.format(password_alies))

        if type(password) != str:
            raise InvalidParamError(
                '"{}" must be a string.'.format(password_alies))

        # TODO more rules, e.g. special character limit, complexity level, etc.
        if is_new:
            if len(password) < self.MIN_LENGTH_OF_PASSWORD or len(password) > self.MAX_LENGTH_OF_PASSWORD:
                raise InvalidParamError(
                    'Password length must between 6 and 20 (included).')

        return self

    def is_not_null(self, object, object_name="object"):
        if object is None:
            raise InvalidParamError('{} cannot be null.'.format(object_name))

    def check_type(self, check_list: List[Check_Tuple]):
        """
        Check parameters types within one list.

        A parameter can pass a check only if
        * the parameter is null when 'nullable' in args
        * or parameter is an instance of the designated type.

        Args:
            check_list (List[Check_Tuple]):
            A list contains the parameters that need a check

        Raises:
            InvalidParamError
        """

        for type, para, name, nullable in check_list:
            if para is None:
                if not nullable:
                    InvalidParamError('{} cannot be null.'.format(name))

            elif not isinstance(para, type):
                raise InvalidParamError(
                    '{} should be a {}.'.format(name, type.__name__))


class GuardFactory:
    def __init__(self) -> None:
        self._check = CheckingCenter()

    @ property
    def check_literaly(self):
        return self._check


myguard = GuardFactory()

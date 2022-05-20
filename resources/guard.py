from errors import InvalidParamError, UnauthorizedError


class CheckingCenter():
    """
    A class as a literal checker.
    Caution: Please note it will only check if the parameters are literaly correct.
    No guarantee whether the input is valid in the database.
    """

    def __init__(self) -> None:
        self.LENGTH_OF_DATASOURCE_ID = 24
        self.MIN_LENGTH_OF_PASSWORD = 6
        self.MAX_LENGTH_OF_PASSWORD = 20

    def user_id(self, user_id: str):
        """
        Check if `user_id` is valid
        Caution: Only check if `user_id` is literally a valid string.
        No guarantee whether `user_id` exists in the database or is reachable.

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

    def datasourse_id(self, datasourse_id: str):
        """
        Check if `datasourse_id` is valid
        Caution: Only check if the `datasourse_id` is literally a valid string.
        No guarantee whether the id of data source exists in the database or is reachable.

        Args:
            id (str): id

        Raises:
            InvalidParamError: raises if `id` is null or not a string

        Returns:
            self: return itself for a stream operation
        """
        if datasourse_id is None or len(datasourse_id) != self.LENGTH_OF_DATASOURCE_ID:
            raise InvalidParamError(
                "Data source id must be a 24-character string")
        return self

    def password(self, password: str, is_new_user: bool):
        """
        Check if `password` is valid
        Caution: Only check if the `password` is literally a valid string.
        No guarantee whether password is correct in the database.

        Args:
            password (str): password
            is_new_user (bool): True if in the registration process

        Raises:
            InvalidParamError: raises if parameter types are not correct or password is too short or too long

        Returns:
            self: return itself for a stream operation
        """

        if type(is_new_user) != bool:
            raise InvalidParamError('"is_new_user" must be boolean.')

        if type(password) != str:
            raise InvalidParamError('Password (string) must be provided.')

        # TODO more rules, e.g. special character limit, complexity level, etc.
        if is_new_user:
            if len(password) < self.MIN_LENGTH_OF_PASSWORD or len(password) > self.MAX_LENGTH_OF_PASSWORD:
                raise InvalidParamError(
                    'Password length must between 6 and 20 (included).')

        return self


class GuardFactory:
    def __init__(self) -> None:
        self._check = CheckingCenter()

    @property
    def check_literaly(self):
        return self._check


myguard = GuardFactory()

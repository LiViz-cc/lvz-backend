from errors import InvalidParamError, UnauthorizedError


class CheckingCenter():
    def __init__(self) -> None:
        self.LENGTH_OF_DATASOURCE_ID = 24

    def user_id(self, user_id: str):
        """
        Check if `user_id` is valid
        Caution: Only check if `user_id` is a valid string.
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
        Caution: Only check if the `datasourse_id` is a valid string.
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
                "Data source id should be a 24-character string")
        return self


class GuardFactory:
    def __init__(self) -> None:
        self._check = CheckingCenter()

    @property
    def check(self):
        return self._check


myguard = GuardFactory()

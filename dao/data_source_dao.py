
from errors import (EmailAlreadyExistsError, ForbiddenError, InvalidParamError,
                    NotFoundError, NotMutableError, UnauthorizedError)
from models import DataSource, DisplaySchema, Project, ShareConfig, User
from mongoengine.errors import DoesNotExist, NotUniqueError, ValidationError
from utils.guard import myguard
import copy


class DataSourceDao:
    def get_by_id(self, id: str) -> DataSource:
        myguard.check_literaly.object_id(id)
        try:
            data_source = DataSource.objects.get(id=id)
        except DoesNotExist:
            raise NotFoundError('data source', 'id={}'.format(id))

        return data_source

    def save(self, data_source: DataSource, *args, **kwargs) -> None:
        try:
            data_source.save(*args, **kwargs)
        except ValidationError as e:
            raise InvalidParamError(e.message)

    def assert_fields_editable(self, mutation_body: dict) -> None:
        if not mutation_body or not isinstance(mutation_body, dict):
            raise InvalidParamError('"mutation_body" is not valid.')

        for field_name in DataSource.uneditable_fields:
            if mutation_body.get(field_name, None):
                raise NotMutableError(DataSource.__name__, field_name)

    def modify(self, data_source: DataSource, mutation_body: dict) -> None:
        # update project
        try:
            data_source.modify(**mutation_body)
        except IndexError as e:
            raise InvalidParamError(e.args)
        except ValidationError as e:
            raise InvalidParamError(e.message)
        except LookupError as e:
            raise InvalidParamError(e.message)

    def get_a_copy_by_id(self, data_source_id: str) -> DataSource:
        """
        Deeply copy a data source. Caution: Cloned document has not been saved yet.

        Args:
            data_source_id (str): data_source that needs to make a deep copy

        Returns:
            DataSource: cloned document (unsaved)
        """
        data_source = self.get_by_id(data_source_id)
        new_data_source = copy.deepcopy(data_source)
        return new_data_source

    def get_a_copy(self, data_source: DataSource) -> DataSource:
        """
        Deeply copy a data source. Caution: Cloned document has not been saved to database yet.

        Args:
            data_source (str): data_source that needs to make a deep copy

        Returns:
            DataSource: cloned document (unsaved)
        """
        new_data_source = copy.deepcopy(data_source)
        return new_data_source

    def delete(self, data_source: DataSource, *args, **kwargs) -> None:
        if data_source:
            myguard.check_literaly.check_type([
                (DataSource, data_source, "Data source", False)
            ])

            # TODO: add more error handling
            try:
                data_source.delete(*args, **kwargs)
            except DoesNotExist as e:
                raise NotFoundError('Data source', 'id={}'.format(
                    getattr(data_source, 'id', 'None')))

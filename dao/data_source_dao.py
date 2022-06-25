

from models import DataSource
from utils.common import *


class DataSourceDao:
    def get_by_id(self, id: str) -> DataSource:
        myguard.check_literaly.object_id(id)
        try:
            data_source = DataSource.objects.get(id=id)
        except DoesNotExist:
            raise NotFoundError('data source', 'id={}'.format(id))

        return data_source

    def save(self, data_source: DataSource) -> None:
        try:
            data_source.save()
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
        except ValidationError as e:
            raise InvalidParamError(e.message)
        except LookupError as e:
            raise InvalidParamError(e.message)

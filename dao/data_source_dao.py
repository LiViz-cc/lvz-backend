

from models import DataSource
from utils.common import *


class DataSourceDao:
    def get_by_id(self, id: str):
        try:
            data_source = DataSource.objects.get(id=id)
        except DoesNotExist:
            raise NotFoundError('data source', 'id={}'.format(id))

        return data_source

    def save(self, data_source: DataSource):
        try:
            data_source.save()
        except ValidationError as e:
            raise InvalidParamError(e.message)

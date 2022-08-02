from typing import List
from errors import (EmailAlreadyExistsError, ForbiddenError, InvalidParamError,
                    NotFinishedYet, NotFoundError, NotMutableError,
                    UnauthorizedError)
from models import DataSource, DisplaySchema, Project, ShareConfig, User
from mongoengine.errors import DoesNotExist, NotUniqueError, ValidationError
from utils.guard import myguard


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

    def get_a_copy(self, data_source: DataSource) -> DataSource:
        """
        Deeply copy a data source. Caution: Cloned document has not been saved to database yet.

        Args:
            data_source (str): data_source that needs to make a deep copy

        Returns:
            DataSource: cloned document (unsaved)
        """
        myguard.check_literaly.check_type([
            (DataSource, data_source, "Data source", False)
        ])

        new_data_source = DataSource()
        for param_name in data_source.property_lists:
            new_data_source[param_name] = data_source[param_name]

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

    def export_slots_to_dicts(self, data_source: DataSource):
        myguard.check_literaly.check_type([
            (DataSource, data_source, "Data source", False)
        ])

        try:
            slots = data_source.slots
        except DoesNotExist as e:
            raise NotFoundError('Data source', 'id={}'.format(
                getattr(data_source, 'id', 'None')))

        if not slots:
            return {}

        # convert documents to SON object and then dictionary
        return [slot.to_mongo().to_dict() for slot in slots]

    def get_by_ids(self, ids: List[int]) -> List[DataSource]:
        # check if input contains duplicate ids
        set_ids = set(ids)
        if len(set_ids) != len(ids):
            raise InvalidParamError('Input contains duplicate ids.')

        # query data source via id
        missing_ids = []
        data_sources = []
        for id in ids:
            try:
                data_source = self.get_by_id(id)
            except NotFoundError as e:
                missing_ids.append(id)
            else:
                data_sources.append(data_source)

        # check if any items are missing from result set
        if missing_ids:
            raise NotFoundError(target='data_source(s)',
                                queries=str(missing_ids))

        return data_sources

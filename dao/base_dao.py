from typing import List
from errors import (EmailAlreadyExistsError, ForbiddenError, InvalidParamError,
                    NotFinishedYet, NotFoundError, NotMutableError,
                    UnauthorizedError)
from mongoengine.errors import DoesNotExist, NotUniqueError, ValidationError
from utils.guard import myguard


class BaseDao:
    def __init__(self, entity_type: type, entity_name: str) -> None:
        self.entity_type = entity_type
        self.entity_name = entity_name

    def get_by_id(self, id: str):
        myguard.check_literaly.object_id(id)
        try:
            item = self.entity_type.objects.get(id=id)
        except DoesNotExist:
            raise NotFoundError(self.entity_name, 'id={}'.format(id))

        return item

    def get_by_ids(self, ids: List[int]):
        # check if input contains duplicate ids
        set_ids = set(ids)
        if len(set_ids) != len(ids):
            raise InvalidParamError('Input contains duplicate ids.')

        # query item via id
        missing_ids = []
        items = []
        for id in ids:
            try:
                item = self.get_by_id(id)
            except NotFoundError as e:
                missing_ids.append(id)
            else:
                items.append(item)

        # check if any items are missing from result set
        if missing_ids:
            raise NotFoundError(target='{}(s)'.format(self.entity_name),
                                queries=str(missing_ids))

        return items

import datetime
from typing import List

from dao import *
from errors import (ForbiddenError, InvalidParamError, NotFoundError,
                    NotMutableError, UnauthorizedError)
from models import *
from mongoengine.errors import DoesNotExist, ValidationError
from utils.common import *


class DisplaySchemaService:
    def __init__(self) -> None:
        self.user_dao = UserDao()
        self.project_dao = ProjectDao()
        self.data_source_dao = DataSourceDao()
        self.display_schema_dao = DisplaySchemaDao()

    def get_display_schemas(self, args, jwt_id) -> List[DisplaySchema]:
        # validate args and construct query dict
        query = {}
        if 'public' in args:
            if args['public'].lower() == 'false':
                query['public'] = False
            if args['public'].lower() == 'true':
                query['public'] = True
        if 'created_by' in args:
            # check authorization
            user = self.user_dao.get_user_by_id(jwt_id)

            if args['created_by'] != str(user.id):
                raise ForbiddenError()
            query['created_by'] = user

        # query display schemas with query dict
        display_schemas = DisplaySchema.objects(**query)

        return display_schemas

    def create_display_schema(self, body: dict, jwt_id: str) -> DisplaySchema:
        # pre-validate params
        linked_project_id = body.get('linked_project', None)
        if not linked_project_id:
            raise InvalidParamError('linked_project cannot be empty.')

        myguard.check_literaly.check_type([
            [str, linked_project_id, 'linked_project']
        ])

        linked_project = self.project_dao.get_by_id(linked_project_id)
        body['linked_project'] = linked_project

        # construct new display schema object
        display_schema = DisplaySchema(**body)

        # set time
        curr_time = datetime.datetime.utcnow
        display_schema.created = curr_time
        display_schema.modified = curr_time

        # set created by
        user = self.user_dao.get_user_by_id(jwt_id)
        display_schema.created_by = user

        # save new display schema
        self.display_schema_dao.save(display_schema)

        return display_schema

    def get_display_schema_by_id(self, id, jwt_id) -> DisplaySchema:
        # query data source via id
        display_schema = self.display_schema_dao.get_by_id(id)

        # check authorization
        if not display_schema.public:
            user = self.user_dao.get_user_by_id(jwt_id)
            if not display_schema.created_by == user:
                raise ForbiddenError()

        return display_schema

    def edit_display_schema(self, id, body, jwt_id) -> DisplaySchema:
        # pre-validate params

        # query project via id
        display_schema = self.display_schema_dao.get_by_id(id)

        # check authorization
        user = self.user_dao.get_user_by_id(jwt_id)

        if display_schema.created_by != user:
            raise ForbiddenError()

        # pre-process params
        linked_project_id = body.get('linked_project', None)
        if linked_project_id:
            linked_project = self.project_dao.get_by_id(linked_project_id)

            # check authorization
            if linked_project.created_by != display_schema.created_by:
                raise ForbiddenError(
                    'linked_project is not created by the user')

            body['linked_project'] = linked_project

        # Forbid changing immutable field
        self.display_schema_dao.assert_fields_editable(body)

        body['modified'] = datetime.datetime.utcnow

        # update project
        self.display_schema_dao.modify(display_schema, body)

        return display_schema

    def delete_display_schema(self, id, jwt_id) -> dict:
        # query project via id
        display_schema = self.display_schema_dao.get_by_id(id)

        # check authorization
        user = self.user_dao.get_user_by_id(jwt_id)

        if display_schema.created_by != user:
            raise ForbiddenError()

        # delete project
        display_schema.delete()

        return {}

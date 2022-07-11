
import datetime
from typing import List

from dao import (DataSourceDao, DisplaySchemaDao, ProjectDao, ShareConfigDao,
                 UserDao)
from errors import (EmailAlreadyExistsError, ForbiddenError, InvalidParamError,
                    NotFoundError, NotMutableError, UnauthorizedError)
from models import DataSource, DisplaySchema, Project, ShareConfig, User
from mongoengine.errors import DoesNotExist, NotUniqueError, ValidationError
from utils.guard import myguard


class DisplaySchemaService:
    def __init__(self) -> None:
        self.user_dao = UserDao()
        self.project_dao = ProjectDao()
        self.data_source_dao = DataSourceDao()
        self.display_schema_dao = DisplaySchemaDao()

    def get_display_schemas(self,
                            is_public: bool,
                            created_by: str,
                            jwt_id: str) -> List[DisplaySchema]:
        # validate args and construct query dict
        query = {}

        if is_public is not None:
            query['public'] = is_public

        if created_by is not None:
            # check authorization
            user = self.user_dao.get_user_by_id(jwt_id)

            if created_by != str(user.id):
                raise ForbiddenError()
            query['created_by'] = user

        # query display schemas with query dict
        display_schemas = DisplaySchema.objects(**query)

        return display_schemas

    def create_display_schema(self,
                              name: str,
                              public: bool,
                              description: str,
                              echarts_option: str,
                              linked_project_id: str,
                              jwt_id: str) -> DisplaySchema:

        user = self.user_dao.get_user_by_id(jwt_id)

        linked_project = self.project_dao.get_by_id(linked_project_id)
        if linked_project.created_by != user:
            raise ForbiddenError()

        # pack body
        body = {}

        param_names = ['name', 'public', 'description',
                       'echarts_option', 'linked_project']
        params = [name, public, description,
                  echarts_option, linked_project]

        for param_name, param in zip(param_names, params):
            if param is not None:
                body[param_name] = param

        # construct new display schema object
        display_schema = DisplaySchema(**body)

        # set time
        curr_time = datetime.datetime.utcnow
        display_schema.created = curr_time
        display_schema.modified = curr_time

        # set created by
        display_schema.created_by = user

        # save new display schema
        self.display_schema_dao.save(display_schema)

        # store old display schema
        # TODO: getattr should be moved to DAO
        try:
            old_display_schema = getattr(
                linked_project, 'display_schema', None)
        except DoesNotExist as e:
            old_display_schema = None

        # register display_schema in project
        self.project_dao.change_display_schema(linked_project, display_schema)

        # delete old display schema
        self.display_schema_dao.delete(old_display_schema)

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

    def edit_display_schema(self,
                            id: str,
                            name: str,
                            public: bool,
                            description: str,
                            echarts_option: str,
                            linked_project_id: str,
                            jwt_id: str) -> DisplaySchema:

        # query project via id
        display_schema = self.display_schema_dao.get_by_id(id)

        # check authorization
        user = self.user_dao.get_user_by_id(jwt_id)

        if display_schema.created_by != user:
            raise ForbiddenError()

        # pack body
        body = {}

        param_names = ['name', 'public', 'description',
                       'echarts_option', 'linked_project']
        params = [name, public, description,
                  echarts_option, linked_project_id]

        for param_name, param in zip(param_names, params):
            if param is not None:
                body[param_name] = param

        # pre-process params
        linked_project_id = body.get('linked_project', None)
        if linked_project_id:
            raise ForbiddenError(
                '"linked_project" cannot be changed after linked. Please create a new display schema.')

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

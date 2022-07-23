import datetime
import json
import os
from typing import List

import utils
from dao.data_source_dao import DataSourceDao
from dao.project_dao import ProjectDao
from dao.user_dao import UserDao
from errors import (ForbiddenError, InvalidParamError, NotFoundError,
                    NotMutableError)
from models import DataSource, User
from models.Project import Project
from mongoengine.errors import DoesNotExist, ValidationError
from utils.guard import myguard

from services.api_fetch_service import ApiFetchService


class DataSourcesService:
    def __init__(self) -> None:
        self.user_dao = UserDao()
        self.project_dao = ProjectDao()
        self.data_source_dao = DataSourceDao()
        self.api_fetch_service = ApiFetchService()

    def _assert_slots(self, slots: list):
        utils.myguard.check_literaly.check_type([
            (list, slots, 'slots', False)
        ])

        available_params = set()
        for slot in slots:
            name = slot.get('name')
            alias = slot.get('alias')

            if name is None:
                raise InvalidParamError(
                    '"name" attribute is missing in a slot in data_source')

            if name in available_params:
                raise InvalidParamError(
                    'Detect duplicate names of slots: {}'.format(name))

            param_name = alias if alias else name
            if param_name in available_params:
                raise InvalidParamError(
                    'Slot "{}" contains duplicate param names or aliases.'.format(name))

            available_params.add(param_name)

    def get_data_sources(self, is_public: bool, created_by: str, jwt_id: str) -> List[DataSource]:
        # validate args and construct query dict
        query = {}

        if is_public is not None:
            query['public'] = is_public

        if created_by is not None:
            # check authorization
            myguard.check_literaly.user_id(jwt_id)
            user = self.user_dao.get_user_by_id(jwt_id)

            if created_by != str(user.id):
                raise ForbiddenError()
            query['created_by'] = created_by

        # query data sources with query dict
        data_sources = DataSource.objects(**query)
        return data_sources

    def get_data_source_by_id(self, id, query: dict, jwt_id) -> DataSource:
        # query data source via id
        data_source = self.data_source_dao.get_by_id(id)

        # check authorization
        if not data_source.public:
            myguard._check.user_id(jwt_id)
            user = self.user_dao.get_user_by_id(jwt_id)

            if not data_source.created_by == user:
                raise ForbiddenError()

        if query:
            slots = self.data_source_dao.export_slots_to_dicts(data_source)

            data = self.api_fetch_service.get_data(
                data_source.url, slots, query)
            data_source.data = data

        return data_source

    def create_data_source(self,
                           name: str,
                           public: bool,
                           description: str,
                           static_data: str,
                           data_type: str,
                           url: str,
                           slots: list,
                           examples: list,
                           jwt_id: str) -> DataSource:

        # check if in development mode
        import os
        env = os.getenv('ENV')
        if env != 'development':
            raise ForbiddenError(
                'Creating a new data source is only allowed in development by admin.')

        # prepare body
        body = {}

        params = [name, public, description,
                  static_data, data_type, url, slots, examples]
        param_names = ['name', 'public',
                       'description', 'static_data', 'data_type', 'url', 'slots', 'examples']

        for param_name, param in zip(param_names, params):
            if param is not None:
                body[param_name] = param

        # check if every slot contains a unique name
        self._assert_slots(slots)

        # pre-validate params
        # construct new data source object
        data_source = DataSource(**body)

        # set time
        curr_time = datetime.datetime.utcnow
        data_source.created = curr_time
        data_source.modified = curr_time

        # set created by
        user = self.user_dao.get_user_by_id(jwt_id)

        data_source.created_by = user

        # save new data source
        self.data_source_dao.save(data_source)

        # update user's reference to share_config
        self.user_dao.add_data_source(user, data_source)

        return data_source

    def edit_data_source(self,
                         id: str,
                         name: str,
                         public: bool,
                         description: str,
                         static_data: str,
                         data_type: str,
                         url: str,
                         slots: list,
                         examples: list,
                         jwt_id) -> DataSource:

        # check if contains uneditable params
        # check if in development mode
        env = os.getenv('ENV')
        if env != 'development':
            if url is not None:
                raise InvalidParamError('"url" cannot be changed.')

            if slots is not None:
                raise InvalidParamError('"slots" cannot be changed.')

        # prepare body
        body = {}

        params = [name, public, description,
                  static_data, data_type, url, slots, examples]
        param_names = ['name', 'public',
                       'description', 'static_data', 'data_type', 'url', 'slots', 'examples']

        for param_name, param in zip(param_names, params):
            if param is not None:
                body[param_name] = param

        # check if every slot contains a unique name
        self._assert_slots(slots)

        # query project via id
        data_source = self.data_source_dao.get_by_id(id)

        # check authorization
        myguard.check_literaly.user_id(jwt_id)

        user = self.user_dao.get_user_by_id(jwt_id)

        if data_source.created_by != user:
            raise ForbiddenError()

        # Forbid changing immutable field
        self.data_source_dao.assert_fields_editable(body)

        body['modified'] = datetime.datetime.utcnow

        # update project
        self.data_source_dao.modify(data_source, body)

        return data_source

    def delete_data_source(self, id, jwt_id) -> dict:
        # query project via id
        data_source = self.data_source_dao.get_by_id(id)

        # check authorization
        user = self.user_dao.get_user_by_id(jwt_id)

        if data_source.created_by != user:
            raise ForbiddenError()

        # delete project
        self.data_source_dao.delete(data_source)

        return {}

    def link_to_project(self, data_source: DataSource, project: Project, jwt_id: str) -> None:
        # TODO: need some tests
        # TODO: need an API to implement it

        user = self.user_dao.get_user_by_id(jwt_id)
        if (data_source.created_by != user) or (project.created_by != user):
            raise ForbiddenError()

        self.project_dao.add_data_source(project, data_source)
        project = self.project_dao.get_by_id(project.pk)
        return project

    def clone_by_id(self, data_source_id: str, jwt_id: str) -> DataSource:
        # get current jwt user
        user = self.user_dao.get_user_by_id(jwt_id)

        # get data_source
        data_source = self.data_source_dao.get_by_id(data_source_id)

        # check authorization
        if not data_source.public and data_source.created_by != user:
            raise ForbiddenError()

        # get a clone
        new_data_source = self.data_source_dao.get_a_copy(data_source)

        # change meta-data
        current_time = datetime.datetime.utcnow
        new_data_source['created_by'] = user
        new_data_source['created'] = current_time
        new_data_source['modified'] = current_time

        self.data_source_dao.save(new_data_source)

        return new_data_source

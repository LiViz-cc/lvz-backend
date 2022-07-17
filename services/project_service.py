import datetime
from typing import List

from dao import (DataSourceDao, DisplaySchemaDao, ProjectDao, ShareConfigDao,
                 UserDao)
from errors import (EmailAlreadyExistsError, ForbiddenError, InvalidParamError,
                    NotFoundError, NotMutableError, UnauthorizedError)

from models import (DataSource, DisplaySchema, Project, ShareConfig, User)
from utils.logger import get_the_logger

logger = get_the_logger()


class ProjectService:
    def __init__(self) -> None:
        self.project_dao = ProjectDao()
        self.user_dao = UserDao()
        self.data_source_dao = DataSourceDao()
        self.display_schema_dao = DisplaySchemaDao()
        self.share_config_dao = ShareConfigDao()

    def get_projects(self,
                     is_public: bool,
                     created_by: str,
                     jwt_id) -> List[Project]:

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

        # query projects with query dict
        projects = Project.objects(**query)

        return projects

    def get_project_by_id(self, id, jwt_id) -> Project:
        # query project via id
        project = self.project_dao.get_by_id(id)

        # check authorization
        if not project.public:
            user = self.user_dao.get_user_by_id(jwt_id)
            if project.created_by != user:
                raise ForbiddenError()

        return project

    def create_project(self,
                       name: str,
                       is_public: bool,
                       data_source_ids: str,
                       display_schema_id: str,
                       jwt_id: str) -> Project:
        # get jwt user
        user = self.user_dao.get_user_by_id(jwt_id)

        # pack body
        body = {'name': name}

        # pre-validate params (is_public)
        if type(is_public) != bool:
            is_public = False
            body['public'] = is_public

        # pre-validate params (data_source_id)
        if data_source_ids:
            if not isinstance(data_source_ids, list):
                raise InvalidParamError('data_sources should be a list.')

            data_source_list = []
            for data_source_id in data_source_ids:
                data_source = self.data_source_dao.get_by_id(data_source_id)

                if not data_source.public:
                    if is_public:
                        raise InvalidParamError(
                            'Cannot create a public project with private data source!')
                    if data_source.created_by.id != user.id:
                        raise ForbiddenError()

                data_source_list.append(data_source)

            body['data_sources'] = data_source_list

        # pre-validate params (display_schema_id)
        if display_schema_id:
            display_schema = self.display_schema_dao.get_by_id(
                display_schema_id)
            if not display_schema.public:
                if is_public:
                    raise InvalidParamError(
                        'Cannot create a public project with private display schema!')
                if display_schema.created_by.id != user.id:
                    raise ForbiddenError()

            body['display_schema'] = display_schema

        # construct new project object
        project = Project(**body)

        # set time
        curr_time = datetime.datetime.utcnow
        project.created = curr_time
        project.modified = curr_time

        # set created by
        project.created_by = user

        # save new project
        self.project_dao.save(project)

        # update user's reference to project
        self.user_dao.add_project(user, project)

        return project

    def edit_project(self, id, public, jwt_id) -> Project:
        # check auth
        user = self.user_dao.get_user_by_id(jwt_id)

        # query project via id
        project = self.project_dao.get_by_id(id)

        if project.created_by != user:
            raise ForbiddenError()

        body = {}

        if public is None:
            raise InvalidParamError('Mutation body cannot be empty.')

        body['modified'] = datetime.datetime.utcnow

        # update project
        self.project_dao.modify(project, body)

        return project

    def delete_project(self, id: str, jwt_id: str) -> dict:
        # check auth
        user = self.user_dao.get_user_by_id(jwt_id)

        # query project via id
        project = self.project_dao.get_by_id(id)

        # check authorization
        if project.created_by != user:
            raise ForbiddenError()

        # delete project
        self.project_dao.delete(project)

        return {}

    def add_data_sources(self, project_id: str, data_source_ids: List[str], jwt_id: str):
        # check authorization
        user = self.user_dao.get_user_by_id(jwt_id)

        # query project
        project = self.project_dao.get_by_id(project_id)
        if project.created_by != user:
            raise ForbiddenError()

        # query data_sources
        data_sources = []

        for data_source_id in data_source_ids:
            data_source = self.data_source_dao.get_by_id(data_source_id)
            # check authorization
            if data_source.created_by != user:
                raise ForbiddenError()
            data_sources.append(data_source)

        self.project_dao.add_data_sources(project, data_sources)

        # re-query project
        project = self.project_dao.get_by_id(project_id)
        return project

    def remove_data_sources(self, project_id: str, data_source_ids: List[str], jwt_id: str):
        # check authorization
        user = self.user_dao.get_user_by_id(jwt_id)

        # query project
        project = self.project_dao.get_by_id(project_id)
        if project.created_by != user:
            raise ForbiddenError()

        # query data_sources
        data_sources = []

        for data_source_id in data_source_ids:
            data_source = self.data_source_dao.get_by_id(data_source_id)
            # check authorization
            if data_source.created_by != user:
                raise ForbiddenError()
            data_sources.append(data_source)

        self.project_dao.remove_data_sources(project, data_sources)

        # re-query project
        project = self.project_dao.get_by_id(project_id)
        return project

    def shallow_copy(self, project_id: str, jwt_id: str) -> Project:
        user = self.user_dao.get_user_by_id(jwt_id)

        # query project
        project = self.project_dao.get_by_id(project_id)
        if project.created_by != user:
            raise ForbiddenError()

        display_schema = getattr(project, 'display_schema', None)

        # get a shallow copy
        new_project = self.project_dao.get_a_shallow_copy(project)

        # change meta-data
        current_time = datetime.datetime.utcnow
        new_project['created_by'] = user
        new_project['created'] = current_time
        new_project['modified'] = current_time

        self.project_dao.save(new_project, force_insert=True)

        # TODO: need a change
        if display_schema:
            new_display_schema = self.display_schema_dao.get_a_copy(
                display_schema)
            self.display_schema_dao.save(new_display_schema)

            new_project.modify(display_schema=new_display_schema)
            new_display_schema.update(linked_project=new_project)

        return new_project

    def link_to_display_schema(self,
                               project_id: str,
                               display_schema_id: str,
                               jwt_id: str) -> Project:

        project = self.project_dao.get_by_id(project_id)
        display_schema = self.display_schema_dao.get_by_id(display_schema_id)
        jwt_user = self.user_dao.get_user_by_id(jwt_id)

        if project.created_by != jwt_user:
            raise ForbiddenError(
                'This project was not created by current user')

        if display_schema.created_by != jwt_user:
            raise ForbiddenError(
                'This display schema was not created by current user')

        old_display_schema = project.display_schema
        old_project = display_schema.linked_project

        if old_display_schema:
            self.display_schema_dao.modify(
                old_display_schema, {'linked_project': None})

        if old_project:
            self.project_dao.modify(
                old_project, {'display_schema': None})

        self.project_dao.modify(
            project, {'display_schema': display_schema})
        self.display_schema_dao.modify(
            display_schema, {'linked_project': project})

        return project

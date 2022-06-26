from typing import List

from dao import *
from errors import NotFinishedYet
from models import *
from utils.common import *

logger = get_the_logger()


class ProjectService:
    def __init__(self) -> None:
        self.project_dao = ProjectDao()
        self.user_dao = UserDao()
        self.data_source_dao = DataSourceDao()
        self.display_schema_dao = DisplaySchemaDao()
        self.share_config_dao = ShareConfigDao()

    def get_projects(self, args, jwt_id) -> List[Project]:
        # validate args and construct query dict
        query = {}
        if 'public' in args:
            if args['public'].lower() == 'false':
                query['public'] = False
            if args['public'].lower() == 'true':
                query['public'] = True

        # TODO: what if 'created_by' not in args? May a user get all projects?

        if 'created_by' in args:
            # check authorization
            user = self.user_dao.get_user_by_id(jwt_id)

            if args['created_by'] != str(user.id):
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

    def create_project(self, body: dict, is_public: bool, data_source_ids: str, display_schema_id: str, user: User) -> Project:
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

    def edit_project(self, id, body, user) -> Project:
        # query project via id
        project = self.project_dao.get_by_id(id)

        if project.created_by != user:
            raise ForbiddenError()

        # Forbid changing immutable field
        self.project_dao.assert_fields_editable(body)

        body['modified'] = datetime.datetime.utcnow

        # update project
        self.project_dao.modify(project, body)

        return project

    def delete_project(self, id, user) -> dict:
        # query project via id
        project = self.project_dao.get_by_id(id)

        # check authorization
        if project.created_by != user:
            raise ForbiddenError()

        # delete project
        project.delete()

        return {}

    def add_data_sources(self, project_id: str, data_source_ids: List[str], jwt_id: str):
        # TODO: need an API to implement it
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
        # TODO: need an API to implement it
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


import utils
from errors import InvalidParamError
from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from services import ProjectService
from utils.guard import myguard
from utils.logger import get_the_logger

from .response_wrapper import response_wrapper

logger = get_the_logger()


class ProjectsResource(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.project_service = ProjectService()

    @response_wrapper
    @jwt_required(optional=True)
    def get(self):
        # get request args dict
        args = request.args
        logger.info('GET all projects with args {}'.format(args))

        jwt_id = get_jwt_identity()

        query_type = args.get('query_type')

        if query_type is None:
            raise InvalidParamError('Please provide "query_type" in query.')

        if query_type == 'id_only':
            # prepare `ids`
            ids = args.get('id')
            if not ids:
                raise InvalidParamError('Please provide "id" in query.')

            utils.myguard.check_literaly.check_type(
                [(str, ids, 'id {}'.format(ids), False)]
            )

            project_ids = ids.split(',')
            # TODO: add check for IDs

            return self.project_service.get_projects_by_ids(project_ids, jwt_id)

        elif query_type == 'filter':
            # prepare `is_public`
            is_public = args.get('is_public')

            # convert is_public to bool if not None
            if is_public is not None:
                is_public = utils.convert_string_to_bool(
                    is_public, 'is_public')

            # prepare `created_by`
            created_by = args.get('created_by')

            # check type
            utils.myguard.check_literaly.check_type([
                (bool, is_public, 'is_public', True),
                (str, created_by, 'created_by', True)
            ])

            return self.project_service.get_projects(is_public, created_by, jwt_id)
        else:
            raise InvalidParamError(
                'Please provide "query_type" in query. Available inputs: "id_only", "filter".')

    @response_wrapper
    @jwt_required()
    def post(self):
        # get request body dict
        body = request.get_json()

        logger.info('POST project with body {}'.format(body))

        param_names = ['name', 'public', 'data_sources',
                       'display_schema', 'clone', 'project']

        name, public, data_source_ids, display_schema_id, clone, project_id = [
            body.get(x) for x in param_names]

        if clone:
            # Clone a project from existed one
            if clone == 'shallow':
                myguard.check_literaly.object_id(project_id, 'project')
                jwt_id = get_jwt_identity()
                return self.project_service.shallow_copy(project_id, jwt_id)
            else:
                raise InvalidParamError('"clone" field only accepts "shallow')
        else:
            # Create a new project
            utils.myguard.check_literaly.check_type([
                (str, name, 'name', False),
                (bool, public, 'public', True),
                (list, data_source_ids,  'data_sources', True),
                (str, display_schema_id,  'display_schema', True)
            ])

            jwt_id = get_jwt_identity()

            return self.project_service.create_project(name, public, data_source_ids, display_schema_id, jwt_id)


class ProjectResource(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.project_service = ProjectService()

    @response_wrapper
    @jwt_required(optional=True)
    def get(self, id):
        user_id = get_jwt_identity()

        return self.project_service.get_project_by_id(id, user_id)

    @response_wrapper
    @jwt_required()
    def put(self, id):
        # get request body dict
        body = request.get_json()

        # get authorization
        jwt_id = get_jwt_identity()

        param_names = ['public']

        public = [body.get(x) for x in param_names]

        return self.project_service.edit_project(id, public, jwt_id)

    @response_wrapper
    @jwt_required()
    def delete(self, id):
        # get authorization
        jwt_id = get_jwt_identity()

        return self.project_service.delete_project(id, jwt_id)


class ProjectDataSourcesResource(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.project_service = ProjectService()

    @response_wrapper
    @jwt_required()
    def put(self, id):
        body = request.get_json()
        data_source_ids = body.get('data_sources', None)
        jwt_id = get_jwt_identity()

        utils.myguard.check_literaly.check_type([
            (list, data_source_ids, 'data_sources', False)
        ])

        return self.project_service.add_data_sources(id, data_source_ids, jwt_id)

    @response_wrapper
    @jwt_required()
    def delete(self, id):
        body = request.get_json()
        data_source_ids = body.get('data_sources', None)
        jwt_id = get_jwt_identity()

        return self.project_service.remove_data_sources(id, data_source_ids, jwt_id)


class ProjectDispalySchemaResource(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.project_service = ProjectService()

    @response_wrapper
    @jwt_required()
    def put(self, id):
        body = request.get_json()
        project_id = id
        display_schema_id = body.get('display_schema')
        jwt_id = get_jwt_identity()

        utils.myguard.check_literaly.check_type([
            (str, display_schema_id, 'display_schema', False)
        ])

        return self.project_service.link_to_display_schema(project_id, display_schema_id, jwt_id)

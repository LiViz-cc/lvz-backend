
from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from services import ProjectService
import utils
from utils.guard import myguard
from utils.logger import get_the_logger
from errors import InvalidParamError

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

        # prepare `is_public`
        is_public = None
        if 'public' in args:
            if args['public'].lower() == 'false':
                is_public = False
            if args['public'].lower() == 'true':
                is_public = True

        # prepare `created_by`
        created_by = args.get('created_by')

        return self.project_service.get_projects(is_public, created_by, jwt_id)

    @response_wrapper
    @jwt_required()
    def post(self):
        # get request body dict
        body = request.get_json()

        logger.info('POST project with body {}'.format(body))

        param_names = ['public', 'data_sources',
                       'display_schema', 'clone', 'project']

        public, data_source_ids, display_schema_id, clone, project_id = [
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
                (bool, public, 'public', True),
                (list, data_source_ids,  'data_sources', True),
                (str, display_schema_id,  'display_schema', True)
            ])

            jwt_id = get_jwt_identity()

            return self.project_service.create_project(public, data_source_ids, display_schema_id, jwt_id)


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

        return self.project_service.add_data_sources(id, data_source_ids, jwt_id)

    @response_wrapper
    @jwt_required()
    def delete(self, id):
        body = request.get_json()
        data_source_ids = body.get('data_sources', None)
        jwt_id = get_jwt_identity()

        return self.project_service.remove_data_sources(id, data_source_ids, jwt_id)


from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from services import ProjectService
from utils.guard import myguard
from utils.jwt import get_current_user
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

        return self.project_service.get_projects(args, jwt_id)

    @response_wrapper
    @jwt_required()
    def post(self):
        # get request body dict
        body = request.get_json()
        body: dict

        logger.info('POST project with body {}'.format(body))

        public = body.get('public', None)
        data_source_ids = body.get('data_sources', None)
        display_schema_id = body.get('display_schema', None)

        myguard.check_literaly.check_type([
            (bool, public, 'public', True),
            (list, data_source_ids,  'data_sources', True),
            (str, display_schema_id,  'display_schema', True)
        ])

        user = get_current_user()

        return self.project_service.create_project(body, public, data_source_ids, display_schema_id, user)


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

        # check authorization
        user = get_current_user()

        return self.project_service.edit_project(id, body, user)

    @response_wrapper
    @jwt_required()
    def delete(self, id):
        # check authorization
        user = get_current_user()

        return self.project_service.delete_project(id, user)


class ProjectDataSourcesResource(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.project_service = ProjectService()

    @response_wrapper
    @jwt_required()
    def put(self, id):
        body = request.get_json()
        data_sources = body.get('data_sources', None)
        jwt_id = get_jwt_identity()

        return self.project_service.add_data_sources(id, data_sources, jwt_id)

    @response_wrapper
    @jwt_required()
    def delete(self, id):
        body = request.get_json()
        data_sources = body.get('data_sources', None)
        jwt_id = get_jwt_identity()

        return self.project_service.remove_data_sources(id, data_sources, jwt_id)

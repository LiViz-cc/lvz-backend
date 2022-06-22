
from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from services.data_source_service import DataSourcesService
from utils.guard import myguard

from .response_wrapper import response_wrapper


class DataSourcesResource(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.data_sources_service = DataSourcesService()

    @response_wrapper
    @jwt_required(optional=True)
    def get(self):
        # get request args dict
        args = request.args
        user_id = get_jwt_identity()

        return self.data_sources_service.get_data_sources(args, user_id)

    @response_wrapper
    @jwt_required()
    def post(self):
        # get request body dict
        body = request.get_json()
        user_id = get_jwt_identity()

        return self.data_sources_service.create_data_source(body, user_id)


class DataSourceResource(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.data_sources_service = DataSourcesService()

    @response_wrapper
    @jwt_required(optional=True)
    def get(self, id):
        myguard._check.object_id(id)
        user_id = get_jwt_identity()

        return self.data_sources_service.get_data_source_by_id(id, user_id)

    @response_wrapper
    @jwt_required(optional=True)
    def put(self, id):
        # get request body dict
        body = request.get_json()
        user_id = get_jwt_identity()

        return self.data_sources_service.edit_data_source(id, body, user_id)

    @response_wrapper
    @jwt_required(optional=True)
    def delete(self, id):
        user_id = get_jwt_identity()

        return self.data_sources_service.delete_data_source(id, user_id)

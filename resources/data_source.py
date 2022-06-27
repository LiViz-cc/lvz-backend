
from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from services.data_source_service import DataSourcesService
from utils.guard import myguard
from utils.logger import get_the_logger

from .response_wrapper import response_wrapper

logger = get_the_logger()


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

        logger.info(
            'GET data_sources with args {} and jwt_id {}'.format(args, user_id))

        return self.data_sources_service.get_data_sources(args, user_id)

    @response_wrapper
    @jwt_required()
    def post(self):
        # get request body dict
        body = request.get_json()
        jwt_id = get_jwt_identity()

        logger.info(
            'POST data_source with body {} and jwt_id {}'.format(body, jwt_id))

        cloning = body.get('clone', None)

        if cloning:
            # create a data source by cloning
            data_source_id = body.get('data_source', None)
            myguard.check_literaly.object_id(data_source_id, 'data_source')
            return self.data_sources_service.clone_by_id(data_source_id, jwt_id)
        else:
            # create a data source with information in JSON body
            return self.data_sources_service.create_data_source(body, jwt_id)


class DataSourceResource(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.data_sources_service = DataSourcesService()

    @response_wrapper
    @jwt_required(optional=True)
    def get(self, id):
        myguard._check.object_id(id)
        user_id = get_jwt_identity()

        logger.info(
            'GET data_source with id {} and jwt_id {}'.format(id, user_id))

        return self.data_sources_service.get_data_source_by_id(id, user_id)

    @response_wrapper
    @jwt_required(optional=True)
    def put(self, id):
        # get request body dict
        body = request.get_json()
        user_id = get_jwt_identity()

        logger.info(
            'PUT data_source with body {} and jwt_id {}'.format(body, user_id))

        return self.data_sources_service.edit_data_source(id, body, user_id)

    @response_wrapper
    @jwt_required(optional=True)
    def delete(self, id):
        user_id = get_jwt_identity()
        logger.info(
            'DELETE data_source with id {} and jwt_id {}'.format(id, user_id))

        return self.data_sources_service.delete_data_source(id, user_id)

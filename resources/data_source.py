
from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from services.data_source_service import DataSourcesService
from utils.guard import myguard
from utils.logger import get_the_logger

from .response_wrapper import response_wrapper
import utils
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
        jwt_id = get_jwt_identity()

        logger.info(
            'GET data_sources with args {} and jwt_id {}'.format(args, jwt_id))

        # prepare `is_public`
        is_public = None
        if 'public' in args:
            if args['public'].lower() == 'false':
                is_public = False
            if args['public'].lower() == 'true':
                is_public = True

        # prepare `created_by`
        created_by = args.get('created_by')

        return self.data_sources_service.get_data_sources(is_public, created_by, jwt_id)

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
            name = body.get('name')
            public = body.get('public')
            description = body.get('description')
            static_data = body.get('namstatic_datae')
            data_type = body.get('data_type')
            url = body.get('url')
            slots = body.get('slots')

            # check type
            utils.myguard.check_literaly.check_type([
                (str, name, 'name', False),
                (bool, public, 'public', True),
                (str, description, 'description', True),
                (str, static_data, 'static_data', True),
                (str, data_type, 'data_type', False)
            ])

            return self.data_sources_service.create_data_source(name, public, description, static_data, data_type, url, slots, jwt_id)


class DataSourceResource(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.data_sources_service = DataSourcesService()

    @response_wrapper
    @jwt_required(optional=True)
    def get(self, id):
        myguard._check.object_id(id)
        query = dict(request.args)
        user_id: str = get_jwt_identity()

        logger.info(
            'GET data_source with id {} and jwt_id {}'.format(id, user_id))

        return self.data_sources_service.get_data_source_by_id(id, query, user_id)

    @response_wrapper
    @jwt_required()
    def put(self, id):
        # get request body dict
        body = request.get_json()
        jwt_id = get_jwt_identity()

        name = body.get('name')
        public = body.get('public')
        description = body.get('description')
        static_data = body.get('namstatic_datae')
        data_type = body.get('data_type')
        url = body.get('url')
        slots = body.get('slots')

        # check type
        # TODO: add check for url and slots for all methods
        utils.myguard.check_literaly.check_type([
            (str, name, 'name', True),
            (bool, public, 'public', True),
            (str, description, 'description', True),
            (str, static_data, 'static_data', True),
            (str, data_type, 'data_type', True)
        ])

        logger.info(
            'PUT data_source {} with body {} and jwt_id {}'.format(id, body, jwt_id))

        myguard.check_literaly.object_id(id, 'data source id')

        return self.data_sources_service.edit_data_source(id, name, public, description, static_data, data_type, url, slots, jwt_id)

    @response_wrapper
    @jwt_required()
    def delete(self, id):
        user_id = get_jwt_identity()
        logger.info(
            'DELETE data_source with id {} and jwt_id {}'.format(id, user_id))

        return self.data_sources_service.delete_data_source(id, user_id)

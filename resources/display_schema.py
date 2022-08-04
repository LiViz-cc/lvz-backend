from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from errors import ForbiddenError
from services import DisplaySchemaService
import utils

from .response_wrapper import response_wrapper


class DisplaySchemasResource(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.display_schema_service = DisplaySchemaService()

    # @response_wrapper
    # @jwt_required(optional=True)
    # def get(self):
    #     # get request args dict
    #     args = request.args
    #     user_id = get_jwt_identity()

    #     # prepare `is_public`
    #     is_public = None
    #     if 'public' in args:
    #         if args['public'].lower() == 'false':
    #             is_public = False
    #         if args['public'].lower() == 'true':
    #             is_public = True

    #     # prepare `created_by`
    #     created_by = args.get('created_by')

    #     return self.display_schema_service.get_display_schemas(is_public, created_by, user_id)

    @response_wrapper
    @jwt_required()
    def post(self):
        # get request body dict
        body = request.get_json()
        user_id = get_jwt_identity()

        param_names = ['name', 'public', 'description',
                       'echarts_option', ]
        name, public, description, echarts_option = [
            body.get(param_name) for param_name in param_names]

        # pre-validate params
        utils.myguard.check_literaly.check_type([
            (str, name, 'name', False),
            (bool, public, 'public', True),
            (str, description, 'description', True),
            (str, echarts_option, 'echarts_option', True)
        ])

        return self.display_schema_service.create_display_schema(name, public, description, echarts_option, user_id)


class DisplaySchemaResource(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.display_schema_service = DisplaySchemaService()

    @response_wrapper
    @jwt_required(optional=True)
    def get(self, id):
        user_id = get_jwt_identity()

        return self.display_schema_service.get_display_schema_by_id(id, user_id)

    @response_wrapper
    @jwt_required(optional=True)
    def put(self, id):
        # get request body dict
        body = request.get_json()
        user_id = get_jwt_identity()

        param_names = ['name', 'public', 'description',
                       'echarts_option', ]
        name, public, description, echarts_option = [
            body.get(param_name) for param_name in param_names]

        # pre-validate params
        utils.myguard.check_literaly.check_type([
            (str, name, 'name', True),
            (bool, public, 'public', True),
            (str, description, 'description', True),
            (str, echarts_option, 'echarts_option', True)]
        )

        return self.display_schema_service.edit_display_schema(id, name, public, description, echarts_option, user_id)

    @response_wrapper
    @jwt_required(optional=True)
    def delete(self, id):
        user_id = get_jwt_identity()

        return self.display_schema_service.delete_display_schema(id, user_id)

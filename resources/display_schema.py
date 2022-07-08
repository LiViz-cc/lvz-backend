from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from errors import ForbiddenError
from services import DisplaySchemaService

from .response_wrapper import response_wrapper


class DisplaySchemasResource(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.display_schema_service = DisplaySchemaService()

    @response_wrapper
    @jwt_required(optional=True)
    def get(self):
        # get request args dict
        args = request.args
        user_id = get_jwt_identity()

        return self.display_schema_service.get_display_schemas(args, user_id)

    @response_wrapper
    @jwt_required()
    def post(self):
        # get request body dict
        body = request.get_json()
        user_id = get_jwt_identity()

        return self.display_schema_service.create_display_schema(body, user_id)


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

        return self.display_schema_service.edit_display_schema(id, body, user_id)

    @response_wrapper
    @jwt_required(optional=True)
    def delete(self, id):
        raise ForbiddenError(
            'Deleting a display schema linked to a project is not allowed')

        user_id = get_jwt_identity()

        return self.display_schema_service.delete_display_schema(id, user_id)

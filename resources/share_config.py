
import utils
from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from services.share_config_service import ShareConfigService
from utils import get_the_logger

from .response_wrapper import response_wrapper

logger = get_the_logger()


class ShareConfigsResource(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.share_config_service = ShareConfigService()

    # @response_wrapper
    # @jwt_required()
    # def get(self):
    #     """
    #     Get all share_configs created by current user

    #     Raises:
    #         NotFoundError: current user not found in database

    #     Returns:
    #         list of ShareConfigs
    #     """

    #     # check authorization
    #     jwt_id = get_jwt_identity()

    #     return self.share_config_service.get_share_configs(jwt_id)

    @response_wrapper
    @jwt_required()
    def post(self):
        # get request body dict
        body = request.get_json()
        body: dict

        # check authorization
        jwt_id = get_jwt_identity()

        # pre-validate params
        name, project_id, password_protected, password = [
            body.get(x) for x in ['name', 'linked_project', 'password_protected', 'password']]

        utils.myguard.check_literaly.check_type([
            (str, name, 'name', False),
            (str, project_id, 'linked_project_id', False),
            (bool, password_protected, 'password_protected', False)
        ])

        return self.share_config_service.create_share_config(jwt_id, name, project_id, password_protected, password)


class ShareConfigResource(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.share_config_service = ShareConfigService()

    @response_wrapper
    @jwt_required(optional=True)
    def get(self, id):
        # get password
        body = request.get_json()
        password = body.get('password')
        if password is not None:
            del body['password']

        return self.share_config_service.get_by_id(id, password=password)

    @response_wrapper
    @jwt_required()
    def put(self, id):
        # check authorization
        jwt_id = get_jwt_identity()

        # pre-validate params
        body = request.get_json()

        password = body.get('password')
        name = body.get('name')

        return self.share_config_service.edit_by_id(id, jwt_id, password=password, name=name)

    @response_wrapper
    @jwt_required()
    def delete(self, id):
        # check authorization
        jwt_id = get_jwt_identity()

        # get password
        body = request.get_json()
        password = body.get('password')

        return self.share_config_service.delete_by_id(id=id, jwt_id=jwt_id, password=password)


class ShareConfigPasswordResource(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.share_config_service = ShareConfigService()

    @response_wrapper
    @jwt_required()
    def post(self, id):
        # check authorization
        jwt_id = get_jwt_identity()

        # get message body
        body = request.get_json()
        old_password = body.get('old_password')
        new_password = body.get('new_password', None)

        return self.share_config_service.change_password(
            id=id,
            jwt_id=jwt_id,
            old_password=old_password,
            new_password=new_password
        )

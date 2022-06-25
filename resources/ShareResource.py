
from flask import Request, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from services.share_config_service import ShareConfigService
from utils import get_current_user, get_the_logger, myguard

from .response_wrapper import response_wrapper

logger = get_the_logger()


class ShareConfigsResource(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.share_config_service = ShareConfigService()

    @response_wrapper
    @jwt_required()
    def get(self):
        """
        Get all share_configs created by current user

        Raises:
            NotFoundError: current user not found in database

        Returns:
            list of ShareConfigs
        """

        # get request args dict
        args = request.args

        # check authorization
        user = get_current_user()

        return self.share_config_service.get_share_configs(args, user)

    @response_wrapper
    @jwt_required()
    def post(self):
        # get request body dict
        body = request.get_json()
        body: dict

        # get creator user
        user = get_current_user()

        # pre-validate params (project)
        project_id = body.get('linked_project', None)
        password_protected = body.get('password_protected', None)
        password = body.get('password', None)

        return self.share_config_service.create_share_config(body, user, project_id, password_protected, password)


class ShareConfigResource(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.share_config_service = ShareConfigService()

    @response_wrapper
    @jwt_required(optional=True)
    def get(self, id):
        # get password
        args = request.args
        password = args.get('password')

        return self.share_config_service.get_by_id(id, password=password)

    @response_wrapper
    @jwt_required()
    def put(self, id):
        current_user = get_current_user()

        # get password
        args = request.args
        password = args.get('password')

        # get message body
        body = request.get_json()

        return self.share_config_service.put_by_id(id, current_user, password=password, body=body)

    @response_wrapper
    @jwt_required()
    def delete(self, id):
        current_user = get_current_user()

        # get password
        args = request.args
        password = args.get('password')

        return self.share_config_service.delete_by_id(id=id, user=current_user, password=password)


class ShareConfigPasswordResource(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.share_config_service = ShareConfigService()

    @response_wrapper
    @jwt_required()
    def post(self, id):
        current_user = get_current_user()

        # get old password
        args = request.args
        old_password = args.get('password')

        # get message body
        body = request.get_json()
        new_password = body.get('password', None)

        return self.share_config_service.change_password(id=id, user=current_user, old_password=old_password, new_password=new_password)

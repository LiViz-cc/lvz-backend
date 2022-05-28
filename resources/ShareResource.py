from datetime import datetime
from logging import exception

from errors import (ForbiddenError, InvalidParamError, NotFinishedYet,
                    NotFoundError, NotMutableError)
from flask import Request, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from models import Project, User
from models.ShareConfig import ShareConfig
from mongoengine.errors import DoesNotExist, ValidationError
from utils.guard import myguard
from utils.share_config_center import ShareConfigCenter

from .response_wrapper import response_wrapper
from werkzeug.exceptions import BadRequest


class ShareConfigsResource(Resource):
    @response_wrapper
    @jwt_required(optional=True)
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

        # validate args and construct query dict
        query = {}

        # check authorization
        user_id = get_jwt_identity()
        myguard.check_literaly.user_id(user_id)

        try:
            user = User.objects.get(id=user_id)
        except DoesNotExist:
            raise NotFoundError('user', 'id={}'.format(user_id))

        query['created_by'] = user

        # query projects with query dict
        share_configs = ShareConfig.objects(**query)

        # query set cannot be modified
        # create a new list for return
        share_configs_list = []

        for share_config in share_configs:
            share_config.desensitize()
            share_configs_list.append(share_config)

        return share_configs_list

    @response_wrapper
    @jwt_required()
    def post(self):
        # get request body dict
        body = request.get_json()
        body: dict

        # get creator user
        user_id = get_jwt_identity()
        myguard.check_literaly.user_id(user_id)

        try:
            user = User.objects.get(id=user_id)
        except DoesNotExist:
            raise NotFoundError('user', 'id={}'.format(user_id))

        # pre-validate params (project)
        project_name = body.get('linked_project', None)

        myguard.check_literaly.object_id(
            project_name, object_name="linked_project")

        try:
            project = Project.objects.get(id=project_name)
        except DoesNotExist:
            raise NotFoundError('project', 'id={}'.format(project_name))

        if project.created_by.id != user.id:
            raise ForbiddenError(
                "Cannot share a project not created by current user.")

        # pre-validate params (password)
        password_protected = body.get('password_protected', None)
        if password_protected is None:
            raise InvalidParamError('"password_protected" should be provided.')

        password = body.get('password', None)
        if password_protected:
            myguard.check_literaly.password(password=password, is_new=True)
        else:
            if password is not None:
                raise InvalidParamError(
                    '"password" should not be provided when "password_protected" is disabled.')

        # construct new project object
        share_config = ShareConfig(**body)

        if password_protected:
            share_config.hash_password()

        # set time
        curr_time = datetime.utcnow
        share_config.created = curr_time
        share_config.modified = curr_time

        # set created by
        share_config.created_by = user

        # save share config
        try:
            share_config.save()
        except ValidationError as e:
            raise InvalidParamError(e.message)

        # update user projects
        try:
            user.update(push__share_configs=share_config)
            project.update(push__share_configs=share_config)
        except ValidationError as e:
            raise InvalidParamError(e.message)

        share_config.desensitize()
        return share_config


class ShareConfigResource(Resource):
    def get_current_user(self) -> User:
        # check authorization
        user_id = get_jwt_identity()
        myguard.check_literaly.user_id(user_id)

        try:
            user = User.objects.get(id=user_id)
        except DoesNotExist:
            raise NotFoundError('user', 'id={}'.format(user_id))

        return user

    @response_wrapper
    @jwt_required(optional=True)
    def get(self, id):
        share_config_center = ShareConfigCenter()

        # get password
        args = request.args
        password = args.get('password')

        return share_config_center.get_by_id(id, password=password)

    @response_wrapper
    @jwt_required()
    def put(self, id):
        current_user = self.get_current_user()
        share_config_center = ShareConfigCenter()

        # get password
        args = request.args
        password = args.get('password')

        # get message body
        body = request.get_json()

        return share_config_center.put_by_id(id, current_user, password=password, body=body)

    @response_wrapper
    @jwt_required()
    def delete(self, id):
        current_user = self.get_current_user()
        share_config_center = ShareConfigCenter()

        # get password
        args = request.args
        password = args.get('password')

        return share_config_center.delete_by_id(id=id, user=current_user, password=password)


class ShareConfigPasswordResource(Resource):
    def get_current_user(self) -> User:
        # check authorization
        user_id = get_jwt_identity()
        myguard.check_literaly.user_id(user_id)

        try:
            user = User.objects.get(id=user_id)
        except DoesNotExist:
            raise NotFoundError('user', 'id={}'.format(user_id))

        return user

    @response_wrapper
    @jwt_required()
    def post(self, id):
        current_user = self.get_current_user()
        share_config_center = ShareConfigCenter()

        # get old password
        args = request.args
        old_password = args.get('password')

        # get message body
        body = request.get_json()
        new_password = body.get('password', None)

        return share_config_center.change_password(id=id, user=current_user, old_password=old_password, new_password=new_password)

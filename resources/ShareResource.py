from datetime import datetime

from errors import (ForbiddenError, InvalidParamError, NotFinishedYet,
                    NotFoundError, NotMutableError)
from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from models import Project, User
from models.ShareConfig import ShareConfig
from mongoengine.errors import DoesNotExist, ValidationError

from .guard import myguard
from .response_wrapper import response_wrapper


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

        return share_configs

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

        # construct new project object
        share_config = ShareConfig(**body)

        # set time
        curr_time = datetime.utcnow
        share_config.created = curr_time
        share_config.modified = curr_time

        # set created by
        share_config.created_by = user

        # save new project
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

        return share_config


class ShareConfigResource(Resource):
    @response_wrapper
    @jwt_required(optional=True)
    def get(self, id):
        myguard.check_literaly.object_id(id)

        try:
            share_config = ShareConfig.objects.get(id=id)
        except DoesNotExist:
            raise NotFoundError('share_configs', 'id={}'.format(id))

        return share_config

    @response_wrapper
    @jwt_required()
    def put(self, id):
        # get request body dict
        body = request.get_json()

        # query project via id
        myguard.check_literaly.object_id(id)

        try:
            share_config = ShareConfig.objects.get(id=id)
        except DoesNotExist:
            raise NotFoundError('share_config', 'id={}'.format(id))

        # check authorization
        user_id = get_jwt_identity()
        myguard.check_literaly.user_id(user_id)

        try:
            user = User.objects.get(id=user_id)
        except DoesNotExist:
            raise NotFoundError('user', 'id={}'.format(user_id))
        if share_config.created_by != user:
            raise ForbiddenError(
                "Cannot edit a share config not created by current user.")

        # Forbid changing immutable field
        for field_name in ShareConfig.uneditable_fields:
            if body.get(field_name, None):
                raise NotMutableError(ShareConfig.__name__, field_name)

        # update modified time
        body["modified"] = datetime.utcnow

        # update project
        try:
            share_config.modify(**body)
        except ValidationError as e:
            raise InvalidParamError(e.message)
        except LookupError as e:
            raise InvalidParamError(e.message)

        return share_config

    @response_wrapper
    @jwt_required(optional=True)
    def delete(self, id):
        # TODO: not finished

        # query project via id
        myguard.check_literaly.object_id(id)

        try:
            share_config = ShareConfig.objects.get(id=id)
        except DoesNotExist:
            raise NotFoundError('share_config', 'id={}'.format(id))

        # check authorization
        user_id = get_jwt_identity()
        myguard.check_literaly.user_id(user_id)

        try:
            user = User.objects.get(id=user_id)
        except DoesNotExist:
            raise NotFoundError('user', 'id={}'.format(user_id))
        if share_config.created_by != user:
            raise ForbiddenError()

        # delete project
        share_config.delete()

        return {}

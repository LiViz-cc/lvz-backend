from datetime import datetime
from logging import exception

from errors import (ForbiddenError, InvalidParamError, NotFinishedYet,
                    NotFoundError, NotMutableError)
from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from models import Project, User
from models.ShareConfig import ShareConfig
from mongoengine.errors import DoesNotExist, ValidationError

from utils.guard import myguard
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
        print(type(share_configs))

        # TODO: do not work with QuerySet???
        for share_config in share_configs:
            print(type(share_config))
            share_config.desensitize()
            try:
                password = getattr(share_config, 'password', None)
                print(password)
            except Exception:
                pass

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

        share_config.desensitize()
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

        share_config.desensitize()
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

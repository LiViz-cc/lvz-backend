from errors import (ForbiddenError, InvalidParamError, NotFinishedYet,
                    NotFoundError)
from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from models import Project, User
from models.ShareConfig import ShareConfig
from mongoengine.errors import DoesNotExist, ValidationError

from .guard import myguard
from .response_wrapper import response_wrapper


class ShareResource:
    @response_wrapper
    @jwt_required(optional=True)
    def get(self, id):
        # TODO: not finished
        raise NotFinishedYet()

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

        return share_config

    @response_wrapper
    @jwt_required()
    def put(self, id):
        # TODO: not finished
        raise NotFinishedYet()

        # get request body dict
        body = request.get_json()

        # pre-validate params

        # query project via id
        myguard.check_literaly.object_id(id)

        try:
            project = Project.objects.get(id=id)
        except DoesNotExist:
            raise NotFoundError('project', 'id={}'.format(id))

        # check authorization
        user_id = get_jwt_identity()
        myguard.check_literaly.user_id(user_id)

        try:
            user = User.objects.get(id=user_id)
        except DoesNotExist:
            raise NotFoundError('user', 'id={}'.format(user_id))
        if project.created_by != user:
            raise ForbiddenError()

        # update project
        try:
            project.modify(**body)
        except ValidationError as e:
            raise InvalidParamError(e.message)

        # TODO update modified

        return project

    @response_wrapper
    @jwt_required()
    def delete(self, id):
        # TODO: not finished
        raise NotFinishedYet()

        # query project via id
        myguard.check_literaly.object_id(id)

        try:
            project = Project.objects.get(id=id)
        except DoesNotExist:
            raise NotFoundError('project', 'id={}'.format(id))

        # check authorization
        user_id = get_jwt_identity()
        myguard.check_literaly.user_id(user_id)

        try:
            user = User.objects.get(id=user_id)
        except DoesNotExist:
            raise NotFoundError('user', 'id={}'.format(user_id))
        if project.created_by != user:
            raise ForbiddenError()

        # delete project
        project.delete()

        return {}

import datetime

from errors import ForbiddenError, InvalidParamError, NotFoundError
from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from models import DataSource, DisplaySchema, Project, User
from mongoengine.errors import DoesNotExist, ValidationError

from .guard import myguard
from .response_wrapper import response_wrapper


class ProjectsResource(Resource):
    @response_wrapper
    @jwt_required(optional=True)
    def get(self):
        # get request args dict
        args = request.args

        # validate args and construct query dict
        query = {}
        if 'public' in args:
            if args['public'].lower() == 'false':
                query['public'] = False
            if args['public'].lower() == 'true':
                query['public'] = True

        if 'created_by' in args:
            # check authorization
            user_id = get_jwt_identity()
            myguard.check.user_id(user_id)

            try:
                user = User.objects.get(id=user_id)
            except DoesNotExist:
                raise NotFoundError('user', 'id={}'.format(user_id))
            if args['created_by'] != str(user.id):
                raise ForbiddenError()
            query['created_by'] = user

        # query projects with query dict
        projects = Project.objects(**query)

        return projects

    @response_wrapper
    @jwt_required()
    def post(self):
        # get request body dict
        body = request.get_json()
        body: dict

        # get creator user
        user_id = get_jwt_identity()
        myguard.check.user_id(user_id)

        try:
            user = User.objects.get(id=user_id)
        except DoesNotExist:
            raise NotFoundError('user', 'id={}'.format(user_id))

        # pre-validate params (is_public)
        public = body.get('public', None)
        if type(public) != bool:
            public = False
            body['public'] = public

        # pre-validate params (data_source_id)
        data_source_id = body.get('data_source', None)
        if data_source_id:
            try:
                data_source = DataSource.objects.get(id=data_source_id)
            except DoesNotExist:
                raise NotFoundError(
                    'data_source', 'id={}'.format(data_source_id))
            if not data_source.public:
                if public:
                    raise InvalidParamError(
                        'Cannot create a public project with private data source!')
                if data_source.created_by.id != user.id:
                    raise ForbiddenError()

        # pre-validate params (display_schema_id)
        display_schema_id = body.get('display_schema', None)
        if display_schema_id:
            try:
                display_schema = DisplaySchema.objects.get(
                    id=display_schema_id)
            except DoesNotExist:
                raise NotFoundError(
                    'display_schema', 'id={}'.format(display_schema_id))
            if not display_schema.public:
                if public:
                    raise InvalidParamError(
                        'Cannot create a public project with private display schema!')
                if display_schema.created_by.id != user.id:
                    raise ForbiddenError()

        # construct new project object
        project = Project(**body)

        # set time
        curr_time = datetime.datetime.utcnow
        project.created = curr_time
        project.modified = curr_time

        # set created by
        project.created_by = user

        # save new project
        try:
            project.save()
        except ValidationError as e:
            raise InvalidParamError(e.message)

        # update user projects
        try:
            user.update(push__projects=project)
        except ValidationError as e:
            raise InvalidParamError(e.message)

        return project


class ProjectResource(Resource):
    @response_wrapper
    @jwt_required(optional=True)
    def get(self, id):
        # query project via id
        try:
            project = Project.objects.get(id=id)
        except DoesNotExist:
            raise NotFoundError('project', 'id={}'.format(id))

        # check authorization
        if not project.public:
            user_id = get_jwt_identity()
            myguard.check.user_id(user_id)

            try:
                user = User.objects.get(id=user_id)
            except DoesNotExist:
                raise NotFoundError('user', 'id={}'.format(user_id))
            if project.created_by != user:
                raise ForbiddenError()

        return project

    @response_wrapper
    @jwt_required()
    def put(self, id):
        # get request body dict
        body = request.get_json()

        # pre-validate params

        # query project via id
        try:
            project = Project.objects.get(id=id)
        except DoesNotExist:
            raise NotFoundError('project', 'id={}'.format(id))

        # check authorization
        user_id = get_jwt_identity()
        myguard.check.user_id(user_id)

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
        # query project via id
        try:
            project = Project.objects.get(id=id)
        except DoesNotExist:
            raise NotFoundError('project', 'id={}'.format(id))

        # check authorization
        user_id = get_jwt_identity()
        myguard.check.user_id(user_id)
        
        try:
            user = User.objects.get(id=user_id)
        except DoesNotExist:
            raise NotFoundError('user', 'id={}'.format(user_id))
        if project.created_by != user:
            raise ForbiddenError()

        # delete project
        project.delete()

        return {}

from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine.errors import DoesNotExist
from .response_wrapper import response_wrapper
import datetime
from models import User, DataSource
from mongoengine.errors import ValidationError, DoesNotExist
from errors import NotFoundError, ForbiddenError, InvalidParamError


class DataSourcesResource(Resource):
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
            if user_id is None:
                raise ForbiddenError()  # TODO maybe should raise UnauthorizedError?
            try:
                user = User.objects.get(id=user_id)
            except DoesNotExist:
                raise NotFoundError('user', 'id={}'.format(user_id))
            if args['created_by'] != str(user.id):
                raise ForbiddenError()
            query['created_by'] = user

        # query data sources with query dict
        data_sources = DataSource.objects(**query)

        return data_sources

    @response_wrapper
    @jwt_required()
    def post(self):
        # get request body dict
        body = request.get_json()

        # pre-validate params

        # construct new data source object
        data_source = DataSource(**body)

        # set time
        curr_time = datetime.datetime.utcnow
        data_source.created = curr_time
        data_source.modified = curr_time

        # set created by
        user_id = get_jwt_identity()
        try:
            user = User.objects.get(id=user_id)
        except DoesNotExist:
            raise NotFoundError('user', 'id={}'.format(user_id))
        data_source.created_by = user

        # save new data source
        try:
            data_source.save()
        except ValidationError as e:
            raise InvalidParamError(e.message)

        return data_source


class DataSourceResource(Resource):
    @response_wrapper
    @jwt_required(optional=True)
    def get(self, id):
        # query data source via id
        try:
            data_source = DataSource.objects.get(id=id)
        except DoesNotExist:
            raise NotFoundError('data source', 'id={}'.format(id))

        # check authorization
        if not data_source.public:
            user_id = get_jwt_identity()
            try:
                user = User.objects.get(id=user_id)
            except DoesNotExist:
                raise NotFoundError('user', 'id={}'.format(user_id))
            if not data_source.created_by == user:
                raise ForbiddenError()

        return data_source

from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine.errors import DoesNotExist
from .response_wrapper import response_wrapper
import datetime
from models import User, DisplaySchema
from mongoengine.errors import ValidationError, DoesNotExist
from errors import NotFoundError, ForbiddenError, InvalidParamError


class DisplaySchemasResource(Resource):
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

        # query display schemas with query dict
        display_schemas = DisplaySchema.objects(**query)

        return display_schemas

    @response_wrapper
    @jwt_required()
    def post(self):
        # get request body dict
        body = request.get_json()

        # pre-validate params

        # construct new display schema object
        display_schema = DisplaySchema(**body)

        # set time
        curr_time = datetime.datetime.utcnow
        display_schema.created = curr_time
        display_schema.modified = curr_time

        # set created by
        user_id = get_jwt_identity()
        try:
            user = User.objects.get(id=user_id)
        except DoesNotExist:
            raise NotFoundError('user', 'id={}'.format(user_id))
        display_schema.created_by = user

        # save new display schema
        try:
            display_schema.save()
        except ValidationError as e:
            raise InvalidParamError(e.message)

        return display_schema


class DisplaySchemaResource(Resource):
    @response_wrapper
    @jwt_required(optional=True)
    def get(self, id):
        # query data source via id
        try:
            display_schema = DisplaySchema.objects.get(id=id)
        except DoesNotExist:
            raise NotFoundError('display schema', 'id={}'.format(id))

        # check authorization
        if not display_schema.public:
            user_id = get_jwt_identity()
            try:
                user = User.objects.get(id=user_id)
            except DoesNotExist:
                raise NotFoundError('user', 'id={}'.format(user_id))
            if not display_schema.created_by == user:
                raise ForbiddenError()

        return display_schema

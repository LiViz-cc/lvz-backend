import datetime
from typing import List

from errors import (ForbiddenError, InvalidParamError, NotFoundError,
                    NotMutableError, UnauthorizedError)
from models import DisplaySchema, User
from mongoengine.errors import DoesNotExist, ValidationError
from utils.guard import myguard


class DisplaySchemaService:

    def get_display_schemas(self, args, jwt_id) -> List[DisplaySchema]:
        # validate args and construct query dict
        query = {}
        if 'public' in args:
            if args['public'].lower() == 'false':
                query['public'] = False
            if args['public'].lower() == 'true':
                query['public'] = True
        if 'created_by' in args:
            # check authorization
            myguard.check_literaly.user_id(jwt_id)

            try:
                user = User.objects.get(id=jwt_id)
            except DoesNotExist:
                raise NotFoundError('user', 'id={}'.format(jwt_id))
            if args['created_by'] != str(user.id):
                raise ForbiddenError()
            query['created_by'] = user

        # query display schemas with query dict
        display_schemas = DisplaySchema.objects(**query)

        return display_schemas

    def create_display_schema(self, body, jwt_id) -> DisplaySchema:
        # pre-validate params

        # construct new display schema object
        display_schema = DisplaySchema(**body)

        # set time
        curr_time = datetime.datetime.utcnow
        display_schema.created = curr_time
        display_schema.modified = curr_time

        # set created by
        myguard.check_literaly.user_id(jwt_id)

        try:
            user = User.objects.get(id=jwt_id)
        except DoesNotExist:
            raise NotFoundError('user', 'id={}'.format(jwt_id))
        display_schema.created_by = user

        # save new display schema
        try:
            display_schema.save()
        except ValidationError as e:
            raise InvalidParamError(e.message)

        return display_schema

    def get_display_schema_by_id(self, id, jwt_id) -> DisplaySchema:
        # query data source via id
        try:
            display_schema = DisplaySchema.objects.get(id=id)
        except DoesNotExist:
            raise NotFoundError('display schema', 'id={}'.format(id))

        # check authorization
        if not display_schema.public:
            myguard.check_literaly.user_id(jwt_id)
            try:
                user = User.objects.get(id=jwt_id)
            except DoesNotExist:
                raise NotFoundError('user', 'id={}'.format(jwt_id))
            if not display_schema.created_by == user:
                raise ForbiddenError()

        return display_schema

    def edit_display_schema(self, id, body, jwt_id) -> DisplaySchema:
        # pre-validate params

        # query project via id
        myguard.check_literaly.object_id(id)

        try:
            display_schema = DisplaySchema.objects.get(id=id)
        except DoesNotExist:
            raise NotFoundError('display_schema', 'id={}'.format(id))

        # check authorization

        myguard.check_literaly.user_id(jwt_id)

        try:
            user = User.objects.get(id=jwt_id)
        except DoesNotExist:
            raise NotFoundError('user', 'id={}'.format(jwt_id))
        if display_schema.created_by != user:
            raise ForbiddenError()

        # Forbid changing immutable field
        for field_name in DisplaySchema.uneditable_fields:
            if body.get(field_name, None):
                raise NotMutableError(DisplaySchema.__name__, field_name)

        body['modified'] = datetime.datetime.utcnow

        # update project
        try:
            display_schema.modify(**body)
        except ValidationError as e:
            raise InvalidParamError(e.message)
        except LookupError as e:
            raise InvalidParamError(e.message)

        return display_schema

    def delete_display_schema(self, id, jwt_id) -> dict:
        # query project via id
        myguard.check_literaly.object_id(id)

        try:
            display_schema = DisplaySchema.objects.get(id=id)
        except DoesNotExist:
            raise NotFoundError('display_schema', 'id={}'.format(id))

        # check authorization

        myguard.check_literaly.user_id(jwt_id)

        try:
            user = User.objects.get(id=jwt_id)
        except DoesNotExist:
            raise NotFoundError('user', 'id={}'.format(jwt_id))
        if display_schema.created_by != user:
            raise ForbiddenError()

        # delete project
        display_schema.delete()

        return {}

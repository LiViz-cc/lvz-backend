from models import DisplaySchema
from utils.common import *


class DisplaySchemaDao:
    def save(self, display_schema: DisplaySchema) -> None:
        myguard.check_literaly.is_not_null(display_schema, 'display_schema')
        try:
            display_schema.save()
        except ValidationError as e:
            raise InvalidParamError(e.message)

    def get_by_id(self, id: str) -> DisplaySchema:
        myguard.check_literaly.object_id(id, 'display_schema')
        try:
            display_schema = DisplaySchema.objects.get(id=id)
        except DoesNotExist:
            raise NotFoundError('display schema', 'id={}'.format(id))

        return display_schema

    def assert_fields_editable(self, mutation_body: dict):
        if not mutation_body or not isinstance(mutation_body, dict):
            raise InvalidParamError('"mutation_body" is not valid.')

        for field_name in DisplaySchema.uneditable_fields:
            if mutation_body.get(field_name, None):
                raise NotMutableError(DisplaySchema.__name__, field_name)

    def modify(self, display_schema: DisplaySchema, body: dict) -> None:
        try:
            display_schema.modify(**body)
        except ValidationError as e:
            raise InvalidParamError(e.message)
        except LookupError as e:
            raise InvalidParamError(e.message)


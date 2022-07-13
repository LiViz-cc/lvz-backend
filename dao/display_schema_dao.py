from errors import (EmailAlreadyExistsError, ForbiddenError, InvalidParamError,
                    NotFoundError, NotMutableError, UnauthorizedError)
from models import DataSource, DisplaySchema, Project, ShareConfig, User
from mongoengine.errors import DoesNotExist, NotUniqueError, ValidationError
from utils.guard import myguard


class DisplaySchemaDao:
    def save(self, display_schema: DisplaySchema, *args, **kwargs) -> None:
        myguard.check_literaly.is_not_null(display_schema, 'display_schema')
        try:
            display_schema.save(*args, **kwargs)
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

    def get_a_copy(self,  display_schema: DisplaySchema) -> DisplaySchema:
        """
        Deeply copy a display schema. Caution: Cloned document has not been saved to database yet.

        Args:
            display_schema (str): display schema that needs a deep copy

        Returns:
            DisplaySchema: cloned document (unsaved)
        """

        myguard.check_literaly.check_type([
            (DisplaySchema, display_schema, "Display Schema", False)
        ])

        new_display_schema = DisplaySchema()
        for param_name in display_schema.property_lists:
            new_display_schema[param_name] = display_schema[param_name]

        return new_display_schema

    def delete(self, display_schema: DisplaySchema, *args, **kwargs) -> None:
        if display_schema:
            myguard.check_literaly.check_type([
                (DisplaySchema, display_schema, "display schema", False)
            ])

            # TODO: add more error handling
            try:
                display_schema.delete(*args, **kwargs)
            except DoesNotExist as e:
                raise NotFoundError('display schema', 'id={}'.format(
                    getattr(display_schema, 'id', 'None')))

from models import DisplaySchema
from utils.common import *


class DisplaySchemaDao:
    def save(display_schema: DisplaySchema):
        try:
            display_schema.save()
        except ValidationError as e:
            raise InvalidParamError(e.message)

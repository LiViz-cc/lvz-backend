from database import db
from errors import (ForbiddenError, InvalidParamError, NotFoundError,
                    NotMutableError)
from mongoengine.errors import DoesNotExist, ValidationError
from mongoengine.fields import (BooleanField, DateTimeField, EmailField,
                                ListField, ReferenceField, StringField)

from . import DataSource, DisplaySchema, Project, ShareConfig, User


class DisplaySchema(db.Document):
    name = StringField(required=True, max_length=50)
    created = DateTimeField(required=True)
    modified = DateTimeField(required=True)
    created_by = ReferenceField(User.__name__)
    public = BooleanField(required=True, default=False)
    description = StringField(required=True, default='', max_length=1000)
    echarts_option = StringField()  # temp, option JSON
    linked_project = ReferenceField(
        Project.__name__, required=True)

    uneditable_fields = ['created', 'modified', 'created_by']

    def save(self, *args, **kwargs):
        try:
            super().save(*args, **kwargs)
        except ValidationError as e:
            raise InvalidParamError(e.message)

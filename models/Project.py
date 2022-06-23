from database import db
from errors import (ForbiddenError, InvalidParamError, NotFoundError,
                    NotMutableError)
from flask_bcrypt import check_password_hash, generate_password_hash
from mongoengine.errors import DoesNotExist, ValidationError
from mongoengine.fields import (BooleanField, DateTimeField, EmailField,
                                ListField, ReferenceField, StringField)

from . import DataSource, DisplaySchema, ShareConfig, User


class Project(db.Document):
    name = StringField(required=True, max_length=50)
    created = DateTimeField(required=True)
    modified = DateTimeField(required=True)
    created_by = ReferenceField(User.__name__)
    public = BooleanField(required=True, default=False)
    description = StringField(required=True, default='', max_length=1000)
    data_source = ListField(db.ReferenceField(DataSource.__name__))
    display_schema = ReferenceField(DisplaySchema.__name__)
    share_configs = ListField(db.ReferenceField(ShareConfig.__name__))

    uneditable_fields = ['created', 'modified', 'created_by']

    def save(self, *args, **kwargs):
        try:
            super().save(*args, **kwargs)
        except ValidationError as e:
            raise InvalidParamError(e.message)

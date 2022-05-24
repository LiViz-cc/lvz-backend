from database import db

from mongoengine.fields import (
    EmailField, StringField, DateTimeField, ListField, ReferenceField, BooleanField)
from . import User, DataSource, DisplaySchema, ShareConfig


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

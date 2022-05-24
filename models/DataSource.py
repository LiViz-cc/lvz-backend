from email.policy import default
from database import db
from mongoengine.fields import (
    EmailField, StringField, DateTimeField, ListField, ReferenceField, BooleanField)

from . import User


class DataSource(db.Document):
    name = StringField(required=True, max_length=50)
    created = DateTimeField(required=True)
    modified = DateTimeField(required=True)
    created_by = ReferenceField(User.__name__)
    public = BooleanField(required=True, default=False)
    description = StringField(required=True, default='', max_length=1000)
    static_data = StringField()  # temp, data JSON
    type = StringField(required=True)
    
    uneditable_fields = ['created', 'modified', 'created_by']

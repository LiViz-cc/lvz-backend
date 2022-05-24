from database import db
from mongoengine.fields import (BooleanField, DateTimeField, EmailField,
                                ListField, ReferenceField, StringField)
from . import User, Project


class DisplaySchema(db.Document):
    name = StringField(required=True, max_length=50)
    created = DateTimeField(required=True)
    modified = DateTimeField(required=True)
    created_by = ReferenceField(User.__name__)
    public = BooleanField(required=True, default=False)
    description = StringField(required=True, default='', max_length=1000)
    echarts_option = StringField()  # temp, option JSON
    linked_project = ReferenceField(Project.__name__, required=True)

    uneditable_fields = ['created', 'modified', 'created_by']

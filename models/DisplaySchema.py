from database import db
from mongoengine.fields import (BooleanField, DateTimeField, EmailField,
                                ListField, ReferenceField, StringField)
from mongoengine import NULLIFY


class DisplaySchema(db.Document):
    name = StringField(required=True, max_length=50)
    created = DateTimeField(required=True)
    modified = DateTimeField(required=True)
    created_by = ReferenceField('User')
    public = BooleanField(required=True, default=False)
    description = StringField(required=True, default='', max_length=1000)
    echarts_option = StringField()  # temp, option JSON
    linked_project = ReferenceField(
        'Project', default=None, null=True)

    uneditable_fields = ['created', 'modified', 'created_by', 'linked_project']

    @property
    def property_lists(self):
        return ['name', 'created', 'modified', 'created_by',
                'public', 'description', 'echarts_option', 'linked_project']

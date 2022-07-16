from database import db
from mongoengine.fields import (BooleanField, DateTimeField, EmailField,
                                ListField, ReferenceField, StringField)


class Project(db.Document):
    name = StringField(required=True, max_length=50)
    created = DateTimeField(required=True)
    modified = DateTimeField(required=True)
    created_by = ReferenceField('User')
    public = BooleanField(required=True, default=False)
    description = StringField(required=True, default='', max_length=1000)

    data_sources = ListField(db.ReferenceField(
        'DataSource', reverse_delete_rule=db.PULL))
    display_schema = ReferenceField(
        'DisplaySchema', default=None, null=True)
    share_configs = ListField(db.ReferenceField(
        'ShareConfig', reverse_delete_rule=db.PULL))

    uneditable_fields = ['created', 'modified', 'created_by',
                         'data_sources', 'share_configs']

    @property
    def property_lists(self):
        return ['name', 'created', 'modified',
                'created_by', 'public', 'description',
                'data_sources', 'display_schema', 'share_configs']


from email.policy import default
from database import db
from mongoengine.fields import (BooleanField, DateTimeField, EmailField,
                                ListField, DictField, ReferenceField, StringField, URLField)


class DataSource(db.Document):
    name = StringField(required=True, max_length=50)
    created = DateTimeField(required=True)
    modified = DateTimeField(required=True)
    created_by = ReferenceField('User')
    public = BooleanField(required=True, default=False)
    description = StringField(required=True, default='', max_length=1000)
    static_data = StringField()  # temp, data JSON
    data_type = StringField(required=True)
    url = URLField(required=True)
    slots = ListField(DictField(required=True), default=[])
    data = DictField(null=True)

    uneditable_fields = ['created', 'modified', 'created_by']

    @property
    def property_lists(self):
        return ['name', 'created', 'modified', 'created_by',
                'public', 'description', 'static_data', 'data_type', 'url', 'slots']

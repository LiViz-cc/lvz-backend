
from database import db
from mongoengine import (EmbeddedDocument, EmbeddedDocumentField,
                         EmbeddedDocumentListField)
from mongoengine.fields import (BooleanField, DateTimeField, DictField,
                                EmailField, ListField, ReferenceField,
                                StringField, URLField)


class DataSourceSlot(EmbeddedDocument):
    name = StringField(required=True, max_length=50)
    slot_type = StringField(required=True, default='string', max_length=50)
    optional = BooleanField(default=False)
    default = StringField(default=None, null=True, max_length=50)
    alias = StringField(default='', max_length=50)

    @property
    def property_lists(self):
        return ['name', 'slot_type', 'optional', 'default', 'alias']


class DataSourceExample(EmbeddedDocument):
    params = DictField(required=True)
    data = DictField(required=True)
    # created = DateTimeField(required=True)


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
    slots = EmbeddedDocumentListField(DataSourceSlot, required=True)
    examples = EmbeddedDocumentListField(
        DataSourceExample, default=[])

    # only used in returned massages
    data = DictField(null=True)

    uneditable_fields = ['created', 'modified', 'created_by']

    @property
    def property_lists(self):
        return ['name', 'created', 'modified', 'created_by',
                'public', 'description', 'static_data', 'data_type',
                'url', 'slots', 'examples']

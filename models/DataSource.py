from email.policy import default
from database import db


class DataSource(db.Document):
    name = db.StringField(required=True, max_length=50)
    created = db.DateTimeField(required=True)
    modified = db.DateTimeField(required=True)
    created_by = db.ReferenceField('User')
    public = db.BooleanField(required=True, default=False)
    description = db.StringField(required=True, default='', max_length=1000)
    static_data = db.StringField()  # temp, data JSON
    type = db.StringField(required=True)
    uneditable_fields = ['created', 'modified', 'created_by']


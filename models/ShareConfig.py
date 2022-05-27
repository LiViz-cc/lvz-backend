from database import db
from flask_bcrypt import check_password_hash, generate_password_hash
from mongoengine.fields import (DateTimeField, EmailField, ListField,
                                ReferenceField, StringField)

from . import Project, User


class ShareConfig(db.Document):
    name = StringField(required=True, max_length=50)
    created = DateTimeField(required=True)
    modified = DateTimeField(required=True)
    created_by = ReferenceField(User.__name__, required=True)
    linked_project = ReferenceField(Project.__name__, required=True)
    description = StringField(required=True, default='', max_length=1000)
    password_protected = db.BooleanField(required=True)
    password = db.StringField(min_length=60, max_length=60)

    uneditable_fields = ['created', 'modified', 'created_by']

    def hash_password(self):
        self.password = generate_password_hash(self.password).decode('utf8')

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def desensitize(self):
        if hasattr(self, 'password'):
            del self.password

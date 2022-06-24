from database import db
from errors import (ForbiddenError, InvalidParamError, NotFoundError,
                    NotMutableError)
from mongoengine.errors import DoesNotExist, ValidationError
from mongoengine.fields import (BooleanField, DateTimeField, EmailField,
                                ListField, ReferenceField, StringField)


class ShareConfig(db.Document):
    name = StringField(required=True, max_length=50)
    created = DateTimeField(required=True)
    modified = DateTimeField(required=True)
    created_by = ReferenceField('User', required=True)
    linked_project = ReferenceField('Project', required=True)
    description = StringField(required=True, default='', max_length=1000)
    password_protected = db.BooleanField(required=True)
    password = db.StringField(min_length=0, max_length=60)

    # fields that are not editable by user
    # notice: these fields are still mutable
    uneditable_fields = ['created', 'modified',
                         'created_by', 'password_protected', 'password']

    # def hash_password(self):
    #     self.password = generate_password_hash(self.password).decode('utf8')

    # TODO: CHANGE TO PLAIN TEXT
    def check_password(self, password):
        return self.password == password

    def desensitize(self):
        if hasattr(self, 'password'):
            del self.password

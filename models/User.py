from dataclasses import fields

from database import db
from errors import (ForbiddenError, InvalidParamError, NotFoundError,
                    NotMutableError)
from flask_bcrypt import check_password_hash, generate_password_hash
from mongoengine.errors import DoesNotExist, ValidationError
from mongoengine.fields import (DateTimeField, EmailField, ListField,
                                ReferenceField, StringField)


class User(db.Document):
    # use email as unique identifier of the user
    email = EmailField(required=True, unique=True)
    # encrypted password, length: 60
    password = StringField(required=True, min_length=60, max_length=60)
    created = DateTimeField(required=True)
    modified = DateTimeField(required=True)
    projects = ListField(
        ReferenceField('Project', reverse_delete_rule=db.PULL))
    data_sources = ListField(
        ReferenceField('DataSource', reverse_delete_rule=db.PULL))

    # field cannot be edited by normal PUT methods
    uneditable_fields = ['email', 'password', 'created',
                         'modified', 'projects', 'data_sources']

    def hash_password(self):
        self.password = generate_password_hash(self.password).decode('utf8')

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def desensitize(self):
        if hasattr(self, 'password'):
            del self.password

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        """
        Please confirm the password is valid before calling this method

        Args:
            password (str): password

        Returns:
            hashed_password (str): hashed password
        """
        return generate_password_hash(password).decode('utf8')


# delete user created projects when delete user
# it may cause troublesome consequences if delete user
# maybe in the future add a field 'enable' to User
# by default, set enable = 0
# if one user againsts the rules, we need to ban it
# just set enable = -1 (reason code)

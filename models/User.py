from dataclasses import fields

from database import db
from flask_bcrypt import check_password_hash, generate_password_hash
from mongoengine.fields import (
    EmailField, StringField, DateTimeField, ListField, ReferenceField)
from models.DataSource import DataSource

from models.ShareConfig import ShareConfig

from . import Project


class User(db.Document):
    # use email as unique identifier of the user
    email = EmailField(required=True, unique=True)
    # encrypted password, length: 60
    password = StringField(required=True, min_length=60, max_length=60)
    created = DateTimeField(required=True)
    modified = DateTimeField(required=True)
    projects = ListField(
        ReferenceField(Project.__name__, reverse_delete_rule=db.PULL))
    data_sources = ListField(
        ReferenceField(DataSource.__name__, reverse_delete_rule=db.PULL))

    uneditable_fields = ['created', 'modified']

    def hash_password(self):
        self.password = generate_password_hash(self.password).decode('utf8')

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def desensitize(self):
        if hasattr(self, 'password'):
            del self.password

    """
    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        self.password = generate_password_hash(self.password).decode('utf8')
    """

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

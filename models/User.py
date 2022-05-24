from database import db
from models.ShareConfig import ShareConfig
from .Project import Project
from flask_bcrypt import generate_password_hash, check_password_hash


class User(db.Document):
    # use email as unique identifier of the user
    email = db.EmailField(required=True, unique=True)
    # encrypted password, length: 60
    password = db.StringField(required=True, min_length=60, max_length=60)
    created = db.DateTimeField(required=True)
    modified = db.DateTimeField(required=True)
    projects = db.ListField(
        db.ReferenceField('Project', reverse_delete_rule=db.PULL))
    share_configs = db.ListField(
        db.ReferenceField('ShareConfig', reverse_delete_rule=db.PULL))

    uneditable_fields = ['created', 'modified']

    def hash_password(self):
        self.password = generate_password_hash(self.password).decode('utf8')

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def desensitize(self):
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

"""
# The cascade for User is dangerous
User.register_delete_rule(Project, 'created_by', db.CASCADE)
User.register_delete_rule(ShareConfig, 'created_by', db.CASCADE)
"""

# TODO: what about other models? should we add cascade for them too?

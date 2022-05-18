from database import db
from .Project import Project
from flask_bcrypt import generate_password_hash, check_password_hash


class User(db.Document):
    # use email as unique identifier of the user
    email = db.EmailField(required=True, unique=True)
    # encrypted password, length: 60
    password = db.StringField(required=True, min_length=60, max_length=60)
    created = db.DateTimeField(required=True)
    modified = db.DateTimeField(required=True)
    # TODO reverse_delete_rule?
    projects = db.ListField(
        db.ReferenceField('Project', reverse_delete_rule=db.PULL))

    def hash_password(self):
        self.password = generate_password_hash(self.password).decode('utf8')

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def desensitize(self):
        del self.password


# delete user created projects when delete user
# it may cause troublesome consequences if delete user
# maybe in the future add a field 'enable' to User
# by default, set enable = 0
# if one user againsts the rules, we need to ban it
# just set enable = -1 (reason code)
User.register_delete_rule(Project, 'created_by', db.CASCADE)
# TODO: what about other models? should we add cascade for them too?

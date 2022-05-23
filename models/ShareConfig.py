from database import db
from flask_bcrypt import generate_password_hash, check_password_hash


class ShareConfig(db.Document):
    name = db.StringField(required=True, max_length=50)
    created = db.DateTimeField(required=True)
    modified = db.DateTimeField(required=True)
    created_by = db.ReferenceField('User', required=True)
    linked_project = db.ReferenceField("Project", required=True)
    description = db.StringField(required=True, default='', max_length=1000)

    # TODO: password-proteced
    """
    password_protected = db.BooleanField(required=True, default=False)
    password = db.StringField(required=True, min_length=60, max_length=60)

    def hash_password(self):
        self.password = generate_password_hash(self.password).decode('utf8')

    def check_password(self, password):
        return check_password_hash(self.password, password)
    """

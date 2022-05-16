from database import db


class ShareConfig(db.Document):
    name = db.StringField(required=True, max_length=50)
    created = db.DateTimeField(required=True)
    modified = db.DateTimeField(required=True)
    description = db.StringField(required=True, default='', max_length=1000)

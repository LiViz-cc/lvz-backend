from database import db


class Project(db.Document):
    name = db.StringField(required=True, max_length=50)
    created = db.DateTimeField(required=True)
    modified = db.DateTimeField(required=True)
    created_by = db.ReferenceField('User')
    public = db.BooleanField(required=True, default=False)
    description = db.StringField(required=True, default='', max_length=1000)
    data_source = db.ReferenceField('DataSource')
    display_schema = db.ReferenceField('DisplaySchema')
    share_config = db.ReferenceField('ShareConfig')

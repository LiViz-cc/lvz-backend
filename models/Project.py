from database import db
from models.DisplaySchema import DisplaySchema
from models.ShareConfig import ShareConfig
from mongoengine import CASCADE


class Project(db.Document):
    name = db.StringField(required=True, max_length=50)
    created = db.DateTimeField(required=True)
    modified = db.DateTimeField(required=True)
    created_by = db.ReferenceField('User')
    public = db.BooleanField(required=True, default=False)
    description = db.StringField(required=True, default='', max_length=1000)
    data_source = db.ListField(db.ReferenceField('DataSource'))
    display_schema = db.ReferenceField('DisplaySchema')
    share_configs = db.ListField(db.ReferenceField('ShareConfig'))


# TODO: register_delete_rule for model Project
Project.register_delete_rule(ShareConfig, "linked_project", CASCADE)
Project.register_delete_rule(DisplaySchema, "linked_project", CASCADE)

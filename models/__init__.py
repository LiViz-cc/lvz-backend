from mongoengine import CASCADE


from .DisplaySchema import DisplaySchema
from .Project import Project
from .ShareConfig import ShareConfig
from .User import User
from .DataSource import DataSource

# TODO: register_delete_rule for model Project
Project.register_delete_rule(ShareConfig, "linked_project", CASCADE)
Project.register_delete_rule(DisplaySchema, "linked_project", CASCADE)

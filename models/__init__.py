from mongoengine import CASCADE

from .ShareConfig import ShareConfig
from .DataSource import DataSource
from .DisplaySchema import DisplaySchema
from .Project import Project
from .User import User


# TODO: register_delete_rule for model Project
Project.register_delete_rule(ShareConfig, "linked_project", CASCADE)
Project.register_delete_rule(DisplaySchema, "linked_project", CASCADE)

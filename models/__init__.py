from mongoengine import CASCADE, NULLIFY, DO_NOTHING, DENY, PULL

from .ShareConfig import ShareConfig
from .DataSource import DataSource
from .DisplaySchema import DisplaySchema
from .Project import Project
from .User import User


# TODO: register_delete_rule for model Project
Project.register_delete_rule(ShareConfig, "linked_project", CASCADE)
# Project.register_delete_rule(DisplaySchema, "linked_project", CASCADE)
DisplaySchema.register_delete_rule(Project, 'display_schema', NULLIFY)
Project.register_delete_rule(DisplaySchema, 'linked_project', NULLIFY)

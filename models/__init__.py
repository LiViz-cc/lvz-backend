from mongoengine import CASCADE

from .DataSource import DataSource
from .DisplaySchema import DisplaySchema
from .Project import Project
from .ShareConfig import ShareConfig
from .User import User

# TODO: register_delete_rule for model Project
Project.register_delete_rule(ShareConfig, "linked_project", CASCADE)
Project.register_delete_rule(DisplaySchema, "linked_project", CASCADE)

"""
# The cascade for User is dangerous
User.register_delete_rule(Project, 'created_by', db.CASCADE)
User.register_delete_rule(ShareConfig, 'created_by', db.CASCADE)
"""

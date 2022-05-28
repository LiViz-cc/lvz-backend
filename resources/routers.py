from flask_restful import Api

from resources.ShareResource import ShareConfigPasswordResource, ShareConfigResource, ShareConfigsResource
from .auth import LoginResource, SignupResource
from .data_source import DataSourceResource, DataSourcesResource
from .display_schema import DisplaySchemaResource, DisplaySchemasResource
from .project import ProjectResource, ProjectsResource
from .user import UserPasswordResource, UserResource


def initialize_routes(api: Api):
    api.add_resource(SignupResource, '/auth/signup')
    api.add_resource(LoginResource, '/auth/login')

    api.add_resource(UserResource, '/users/<id>')
    api.add_resource(UserPasswordResource, '/users/<id>/password')

    # TODO: detailed instructions needed
    api.add_resource(DataSourcesResource, '/data_sources')
    api.add_resource(DataSourceResource, '/data_sources/<id>')

    api.add_resource(DisplaySchemasResource, '/display_schemas')
    api.add_resource(DisplaySchemaResource, '/display_schemas/<id>')

    api.add_resource(ProjectsResource, '/projects')
    api.add_resource(ProjectResource, '/projects/<id>')

    api.add_resource(ShareConfigsResource, "/share_configs/")
    api.add_resource(ShareConfigResource, "/share_configs/<id>")
    api.add_resource(ShareConfigPasswordResource,
                     "/share_configs/<id>/password")

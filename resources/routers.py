from flask_restful import Api

from resources.share_instance import ShareInstanceResource

from .auth import LoginResource, SignupResource
from .data_source import DataSourceResource, DataSourcesResource
from .display_schema import DisplaySchemaResource, DisplaySchemasResource
from .project import (ProjectDataSourcesResource, ProjectDispalySchemaResource, ProjectResource,
                      ProjectsResource)
from .root import RootResource
from .share_config import (ShareConfigPasswordResource, ShareConfigResource,
                           ShareConfigsResource)
from .user import UserPasswordResource, UserResetResource, UserResource, UserUsernameResource


def initialize_routes(api: Api):
    api.add_resource(RootResource, '/')

    api.add_resource(SignupResource, '/auth/signup')
    api.add_resource(LoginResource, '/auth/login')

    api.add_resource(UserResource, '/users/<id>')
    api.add_resource(UserPasswordResource, '/users/<id>/password')
    api.add_resource(UserResetResource, '/users/<id>/reset')
    api.add_resource(UserUsernameResource, '/users/<id>/username')

    # TODO: detailed instructions needed
    api.add_resource(DataSourcesResource, '/data_sources')
    api.add_resource(DataSourceResource, '/data_sources/<id>')

    api.add_resource(DisplaySchemasResource, '/display_schemas')
    api.add_resource(DisplaySchemaResource, '/display_schemas/<id>')

    api.add_resource(ProjectsResource, '/projects')
    api.add_resource(ProjectResource, '/projects/<id>')

    api.add_resource(ProjectDataSourcesResource,
                     '/projects/<id>/data_sources')
    api.add_resource(ProjectDispalySchemaResource,
                     '/projects/<id>/display_schema')

    api.add_resource(ShareConfigsResource, '/share_configs/')
    api.add_resource(ShareConfigResource, '/share_configs/<id>')
    api.add_resource(ShareConfigPasswordResource,
                     '/share_configs/<id>/password')

    api.add_resource(ShareInstanceResource, '/share_instances/<id>')

from .auth import SignupResource, LoginResource
from .user import UserResource
from .data_source import DataSourcesResource, DataSourceResource
from .display_schema import DisplaySchemasResource, DisplaySchemaResource
from .project import ProjectsResource, ProjectResource


def initialize_routes(api):
    api.add_resource(SignupResource, '/auth/signup')
    api.add_resource(LoginResource, '/auth/login')

    api.add_resource(UserResource, '/users/<id>')

    api.add_resource(DataSourcesResource, '/data_sources')
    api.add_resource(DataSourceResource, '/data_sources/<id>')

    api.add_resource(DisplaySchemasResource, '/display_schemas')
    api.add_resource(DisplaySchemaResource, '/display_schemas/<id>')

    api.add_resource(ProjectsResource, '/projects')
    api.add_resource(ProjectResource, '/projects/<id>')

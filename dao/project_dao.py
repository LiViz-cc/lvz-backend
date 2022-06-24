
from errors import *
from models import DataSource, DisplaySchema, Project, ShareConfig, User
from utils.common import *


class ProjectDao:
    def add_data_source(self, project: Project, data_source: DataSource):
        myguard.check_literaly.is_not_null(project, 'Project')
        myguard.check_literaly.is_not_null(data_source, 'DataSource')

        try:
            self.update(push__data_sources=data_source)
        except ValidationError as e:
            raise InvalidParamError(e.message)

    def add_share_config(self, project: Project, share_config: ShareConfig):
        myguard.check_literaly.is_not_null(project, 'Project')
        myguard.check_literaly.is_not_null(share_config, 'ShareConfig')

        try:
            self.update(push__share_config=share_config)
        except ValidationError as e:
            raise InvalidParamError(e.message)

    def save(self, project: Project):
        myguard.check_literaly.is_not_null(project, 'Project')

        try:
            project.save()
        except ValidationError as e:
            raise InvalidParamError(e.message)

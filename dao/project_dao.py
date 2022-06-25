
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

    def get_by_id(self, id) -> Project:
        # query project via id
        myguard.check_literaly.object_id(id)

        try:
            project = Project.objects.get(id=id)
        except DoesNotExist:
            raise NotFoundError('project', 'id={}'.format(id))

        return project

    def assert_fields_editable(self, body: dict) -> None:
        for field_name in Project.uneditable_fields:
            if body.get(field_name, None):
                raise NotMutableError(Project.__name__, field_name)

    def modify(self, project: Project, body: dict) -> None:
        try:
            project.modify(**body)
        except ValidationError as e:
            raise InvalidParamError(e.message)
        except LookupError as e:
            raise InvalidParamError(e.message)

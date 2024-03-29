
from typing import List
from dao.base_dao import BaseDao
from errors import (EmailAlreadyExistsError, ForbiddenError, InvalidParamError,
                    NotFoundError, NotMutableError, UnauthorizedError)
from models import DataSource, DisplaySchema, Project, ShareConfig, User
from mongoengine.errors import DoesNotExist, NotUniqueError, ValidationError
from utils.guard import myguard


class ProjectDao(BaseDao):
    def __init__(self, entity_type: type = Project, entity_name: str = 'project') -> None:
        super().__init__(entity_type, entity_name)

    def add_data_source(self, project: Project, data_source: DataSource):
        # literally check input
        myguard.check_literaly.is_not_null(project, 'Project')
        myguard.check_literaly.is_not_null(data_source, 'DataSource')

        # add item
        try:
            project.update(push__data_sources=data_source)
        except ValidationError as e:
            raise InvalidParamError(e.message)

    def add_data_sources(self, project: Project, data_sources: List[DataSource]):
        # literally check input
        myguard.check_literaly.is_not_null(project, 'Project')
        for data_source in data_sources:
            myguard.check_literaly.is_not_null(data_source, 'DataSource')

        # assert no provided data_sources already in project
        # TODO: need a refine for performance
        data_sources_in_project = set(getattr(project, 'data_sources', None))
        for data_source in data_sources:
            if data_source in data_sources_in_project:
                raise InvalidParamError(
                    'data_source {} already in project {}'.format(data_source.pk, project.pk))

        # add all
        try:
            project.update(push_all__data_sources=data_sources)
        except ValidationError as e:
            raise InvalidParamError(e.message)

    def remove_data_source(self, project: Project, data_source: DataSource):
        # literally check input
        myguard.check_literaly.is_not_null(project, 'Project')
        myguard.check_literaly.is_not_null(data_source, 'DataSource')

        # assert all provided data_sources already in project
        if data_source not in getattr(project, 'data_sources', None):
            raise InvalidParamError(
                'data_source {} not in project {}'.format(data_source.pk, project.pk))

        # add item
        try:
            project.update(pull__data_sources=data_source)
        except ValidationError as e:
            raise InvalidParamError(e.message)

    def remove_data_sources(self, project: Project, data_sources: List[DataSource]):
        # literally check input
        myguard.check_literaly.is_not_null(project, 'Project')
        data_sources_in_project = set(getattr(project, 'data_sources', None))
        for data_source in data_sources:
            myguard.check_literaly.is_not_null(data_source, 'DataSource')

        # assert all provided data_sources already in project
        # TODO: need a refine for performance
        for data_source in data_sources:
            if data_source not in data_sources_in_project:
                raise InvalidParamError(
                    'data_source {} not in project {}'.format(data_source.pk, project.pk))

        # add all
        try:
            project.update(pull_all__data_sources=data_sources)
        except ValidationError as e:
            raise InvalidParamError(e.message)

    def add_share_config(self, project: Project, share_config: ShareConfig):
        myguard.check_literaly.is_not_null(project, 'Project')
        myguard.check_literaly.is_not_null(share_config, 'ShareConfig')

        try:
            project.update(push__share_configs=share_config)
        except ValidationError as e:
            raise InvalidParamError(e.message)

    def save(self, project: Project, *args, **kwargs):
        myguard.check_literaly.is_not_null(project, 'Project')

        try:
            project.save(*args, **kwargs)
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

    def change_display_schema(self, project: Project, display_schema: DisplaySchema):
        # register new display schema in project
        body = {'display_schema': display_schema}
        self.modify(project, body)

    def get_a_shallow_copy(self, project: Project) -> Project:
        """
        Shallowly copy a project. Caution: Cloned document has not been saved to database yet.

        Args:
            project (Project): project that needs a shallow copy

        Returns:
            Project: cloned document (unsaved)
        """

        myguard.check_literaly.check_type([
            (Project, project, "Project", False)
        ])

        new_project = Project()
        for param_name in project.property_lists:
            new_project[param_name] = project[param_name]

        return new_project

    def delete(self, project: Project, *args, **kwargs) -> None:
        if project:
            myguard.check_literaly.check_type([
                (Project, project, "project", False)
            ])

            # TODO: add more error handling
            try:
                project.delete(*args, **kwargs)
            except DoesNotExist as e:
                raise NotFoundError('project', 'id={}'.format(
                    getattr(project, 'id', 'None')))

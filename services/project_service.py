import datetime
from typing import List

from errors import (ForbiddenError, InvalidParamError, NotFoundError,
                    NotMutableError)
from models import DataSource, DisplaySchema, Project, User
from mongoengine.errors import DoesNotExist, ValidationError
from utils.guard import myguard
from utils.logger import get_the_logger


class ProjectService:
    def get_projects(self, args, jwt_id) -> List[Project]:
        # validate args and construct query dict
        query = {}
        if 'public' in args:
            if args['public'].lower() == 'false':
                query['public'] = False
            if args['public'].lower() == 'true':
                query['public'] = True

        # TODO: what if 'created_by' not in args? May a user get all projects?

        if 'created_by' in args:
            # check authorization
            myguard.check_literaly.user_id(jwt_id)

            try:
                user = User.objects.get(id=jwt_id)
            except DoesNotExist:
                raise NotFoundError('user', 'id={}'.format(jwt_id))
            if args['created_by'] != str(user.id):
                raise ForbiddenError()
            query['created_by'] = user

        # query projects with query dict
        projects = Project.objects(**query)

        return projects

    def get_project_by_id(self, id, user_id) -> Project:
        # query project via id
        myguard.check_literaly.object_id(id)

        try:
            project = Project.objects.get(id=id)
        except DoesNotExist:
            raise NotFoundError('project', 'id={}'.format(id))

        # check authorization
        if not project.public:
            myguard.check_literaly.user_id(user_id)

            try:
                user = User.objects.get(id=user_id)
            except DoesNotExist:
                raise NotFoundError('user', 'id={}'.format(user_id))
            if project.created_by != user:
                raise ForbiddenError()

        return project

    def create_project(self, body: dict, is_public: bool, data_source_ids: str, display_schema_id: str, user: User) -> Project:
        # pre-validate params (is_public)
        if type(is_public) != bool:
            is_public = False
            body['public'] = is_public

        # pre-validate params (data_source_id)

        if data_source_ids:
            for data_source_id in data_source_ids:
                try:
                    data_source = DataSource.objects.get(id=data_source_id)
                except DoesNotExist:
                    raise NotFoundError(
                        'data_source', 'id={}'.format(data_source_id))
                if not data_source.public:
                    if is_public:
                        raise InvalidParamError(
                            'Cannot create a public project with private data source!')
                    if data_source.created_by.id != user.id:
                        raise ForbiddenError()

        # pre-validate params (display_schema_id)

        if display_schema_id:
            try:
                display_schema = DisplaySchema.objects.get(
                    id=display_schema_id)
            except DoesNotExist:
                raise NotFoundError(
                    'display_schema', 'id={}'.format(display_schema_id))
            if not display_schema.public:
                if is_public:
                    raise InvalidParamError(
                        'Cannot create a public project with private display schema!')
                if display_schema.created_by.id != user.id:
                    raise ForbiddenError()

        # construct new project object
        project = Project(**body)

        # set time
        curr_time = datetime.datetime.utcnow
        project.created = curr_time
        project.modified = curr_time

        # set created by
        project.created_by = user

        # save new project
        try:
            project.save()
        except ValidationError as e:
            raise InvalidParamError(e.message)

        # update user's reference to project
        try:
            user.update(push__projects=project)
        except ValidationError as e:
            raise InvalidParamError(e.message)

        return project

    def edit_project(self, id, body, user) -> Project:
        # query project via id
        myguard.check_literaly.object_id(id)

        try:
            project = Project.objects.get(id=id)
        except DoesNotExist:
            raise NotFoundError('project', 'id={}'.format(id))

        if project.created_by != user:
            raise ForbiddenError()

        # Forbid changing immutable field
        for field_name in Project.uneditable_fields:
            if body.get(field_name, None):
                raise NotMutableError(Project.__name__, field_name)

        body['modified'] = datetime.datetime.utcnow

        # update project
        try:
            project.modify(**body)
        except ValidationError as e:
            raise InvalidParamError(e.message)
        except LookupError as e:
            raise InvalidParamError(e.message)

        return project

    def delete_project(self, id, user) -> dict:
        # query project via id
        myguard.check_literaly.object_id(id)

        try:
            project = Project.objects.get(id=id)
        except DoesNotExist:
            raise NotFoundError('project', 'id={}'.format(id))

        # check authorization
        if project.created_by != user:
            raise ForbiddenError()

        # delete project
        project.delete()

        return {}

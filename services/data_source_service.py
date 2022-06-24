import datetime
from typing import List
from dao.data_source_dao import DataSourceDao
from dao.project_dao import ProjectDao
from dao.user_dao import UserDao

from errors import (ForbiddenError, InvalidParamError, NotFoundError,
                    NotMutableError)
from models import DataSource, User
from models.Project import Project
from mongoengine.errors import DoesNotExist, ValidationError
from utils.guard import myguard


class DataSourcesService:
    def __init__(self) -> None:
        self.user_dao = UserDao()
        self.project_dao = ProjectDao()
        self.data_source_dao = DataSourceDao()

    def get_data_sources(self, args, jwt_id) -> List[DataSource]:
        # validate args and construct query dict
        query = {}
        if 'public' in args:
            if args['public'].lower() == 'false':
                query['public'] = False
            if args['public'].lower() == 'true':
                query['public'] = True
        if 'created_by' in args:
            # check authorization
            myguard.check_literaly.user_id(jwt_id)
            user = self.user_dao.get_user_by_id(jwt_id)

            if args['created_by'] != str(user.id):
                raise ForbiddenError()
            query['created_by'] = user

        # query data sources with query dict
        data_sources = DataSource.objects(**query)
        return data_sources

    def get_data_source_by_id(self, id, jwt_id) -> DataSource:
        # query data source via id
        data_source = self.data_source_dao.get_by_id(id)

        # check authorization
        if not data_source.public:
            myguard._check.user_id(jwt_id)
            user = self.user_dao.get_user_by_id(jwt_id)

            if not data_source.created_by == user:
                raise ForbiddenError()

        return data_source

    def create_data_source(self, body, jwt_id) -> DataSource:
        # pre-validate params
        # construct new data source object
        data_source = DataSource(**body)

        # set time
        curr_time = datetime.datetime.utcnow
        data_source.created = curr_time
        data_source.modified = curr_time

        # set created by

        myguard._check.user_id(jwt_id)

        try:
            user = User.objects.get(id=jwt_id)
        except DoesNotExist:
            raise NotFoundError('user', 'id={}'.format(jwt_id))
        user: User
        data_source.created_by = user

        # save new data source
        try:
            data_source.save()
        except ValidationError as e:
            raise InvalidParamError(e.message)

        # update user's reference to share_config
        try:
            user.update(push__data_sources=data_source)
        except ValidationError as e:
            raise InvalidParamError(e.message)

        return data_source

    def edit_data_source(self, id, body, jwt_id) -> DataSource:
        # pre-validate params

        # query project via id
        myguard.check_literaly.object_id(id)

        try:
            data_source = DataSource.objects.get(id=id)
        except DoesNotExist:
            raise NotFoundError('data_source', 'id={}'.format(id))

        # check authorization

        myguard.check_literaly.user_id(jwt_id)

        try:
            user = User.objects.get(id=jwt_id)
        except DoesNotExist:
            raise NotFoundError('user', 'id={}'.format(jwt_id))

        if data_source.created_by != user:
            raise ForbiddenError()

        # Forbid changing immutable field
        for field_name in DataSource.uneditable_fields:
            if body.get(field_name, None):
                raise NotMutableError(DataSource.__name__, field_name)

        body['modified'] = datetime.datetime.utcnow

        # update project
        try:
            data_source.modify(**body)
        except ValidationError as e:
            raise InvalidParamError(e.message)
        except LookupError as e:
            raise InvalidParamError(e.message)

        return data_source

    def delete_data_source(self, id, user_id) -> dict:
        # query project via id
        myguard.check_literaly.object_id(id)

        try:
            data_source = DataSource.objects.get(id=id)
        except DoesNotExist:
            raise NotFoundError('data_source', 'id={}'.format(id))

        # check authorization
        myguard.check_literaly.user_id(user_id)

        try:
            user = User.objects.get(id=user_id)
        except DoesNotExist:
            raise NotFoundError('user', 'id={}'.format(user_id))

        if data_source.created_by != user:
            raise ForbiddenError()

        # delete project
        data_source.delete()

        return {}

    def link_to_project(self, data_source: DataSource, project: Project, jwt_id: str) -> None:
        # TODO: need test

        user = self.user_dao.get_user_by_id(jwt_id)
        if (data_source.created_by != user) or (project.created_by != user):
            raise ForbiddenError()

        self.project_dao.add_data_source(project, data_source)

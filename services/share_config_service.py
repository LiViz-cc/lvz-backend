import datetime
from typing import List

from dao import (DataSourceDao, DisplaySchemaDao, ProjectDao, ShareConfigDao,
                 UserDao)
from errors import (EmailAlreadyExistsError, ForbiddenError, InvalidParamError,
                    NotFoundError, NotMutableError, UnauthorizedError)
from models import DataSource, DisplaySchema, Project, ShareConfig, User
from utils.guard import myguard
from utils.logger import get_the_logger

logger = get_the_logger()


class ShareConfigService:
    def __init__(self) -> None:
        self.share_config_dao = ShareConfigDao()
        self.project_dao = ProjectDao()
        self.user_dao = UserDao()

    def get_share_configs(self, jwt_id) -> List[ShareConfig]:
        # TODO: accept query

        # get auth
        user = self.user_dao.get_user_by_id(jwt_id)

        # validate args and construct query dict
        query = {'created_by': user}

        # query projects with query dict
        share_configs = ShareConfig.objects(**query)

        logger.info("Query processed. Detail: {}".format(query))
        return share_configs

    def get_by_id(self, id: str, password: str) -> ShareConfig:
        # query project via id
        share_config = self.share_config_dao.get_by_id(id)

        # check if password-protected
        if share_config.password_protected:
            self.share_config_dao.assert_password_match(share_config, password)

        # remove password field for return
        # share_config.desensitize()
        return share_config

    def create_share_config(self,
                            jwt_id: str,
                            name: str,
                            project_id: str,
                            password_protected: bool,
                            password: str):

        project = self.project_dao.get_by_id(project_id)

        # get auth
        user = self.user_dao.get_user_by_id(jwt_id)

        if project.created_by != user:
            raise ForbiddenError(
                "Cannot share a project not created by current user.")

        # pre-validate params (password)
        if password_protected is None:
            raise InvalidParamError('"password_protected" should be provided.')

        if password_protected:
            myguard.check_literaly.password(password=password, is_new=True)
        else:
            # do not provide password if password_protected is False
            if password is not None:
                raise InvalidParamError(
                    '"password" should not be provided when "password_protected" is disabled.')

        # pack body
        body = {}

        param_names = ['name', 'linked_project',
                       'password_protected', 'password']
        params = [name, project_id, password_protected, password]

        for param_name, param in zip(param_names, params):
            if param is not None:
                body[param_name] = param

        # construct new project object
        share_config = ShareConfig(**body)

        # set time
        curr_time = datetime.datetime.utcnow
        share_config.created = curr_time
        share_config.modified = curr_time

        # set created by
        share_config.created_by = user

        # save share config
        self.share_config_dao.save(share_config)

        # update user's and project's reference to share_config
        self.project_dao.add_share_config(project, share_config)

        # share_config.desensitize()
        return share_config

    def edit_by_id(self, id: str, jwt_id: str, password: str, name: str) -> ShareConfig:
        # query project via id
        share_config = self.share_config_dao.get_by_id(id)

        # get auth
        user = self.user_dao.get_user_by_id(jwt_id)

        if share_config.created_by != user:
            raise ForbiddenError(
                "Cannot edit a share config not created by current user.")

        # check if password-protected
        self.share_config_dao.assert_password_match(share_config, password)

        body = {'name': name}

        # update modified time
        body["modified"] = datetime.datetime.utcnow

        # update project
        self.share_config_dao.modify(share_config, body)

        # share_config.desensitize()
        return share_config

    def delete_by_id(self, id: str, jwt_id: str, password: str) -> dict:
        # query project via id
        share_config = self.share_config_dao.get_by_id(id)

        # get auth
        user = self.user_dao.get_user_by_id(jwt_id)

        if share_config.created_by != user:
            raise ForbiddenError()

        # check if password-protected
        self.share_config_dao.assert_password_match(share_config, password)

        # delete project
        self.share_config_dao.delete(share_config)

        return {}

    def change_password(self,
                        id: str,
                        jwt_id: str,
                        old_password: str,
                        new_password: str,
                        ) -> ShareConfig:
        # query project via id
        share_config = self.share_config_dao.get_by_id(id)

        # get auth
        user = self.user_dao.get_user_by_id(jwt_id)

        if share_config.created_by != user:
            raise ForbiddenError()

        modifing_dict = {}

        # check if password-protected
        if share_config.password_protected:
            if new_password is not None:
                '''protected_to_protected'''
                self.share_config_dao.assert_password_match(
                    share_config, old_password)

                myguard.check_literaly.password(
                    new_password, is_new=True, password_alies='new_password')
                modifing_dict.update({'password': new_password})

            else:
                '''protected_to_not_protected'''
                self.share_config_dao.assert_password_match(
                    share_config, old_password)

                modifing_dict.update({'password_protected': False})

        else:
            '''not_protected_to_protected'''
            myguard.check_literaly.password(
                new_password, is_new=True, password_alies='new_password')
            modifing_dict.update({'password': new_password,
                                  'password_protected': True})

        modifing_dict['modified'] = datetime.datetime.utcnow
        # save share config
        self.share_config_dao.modify(share_config, modifing_dict)

        # share_config.desensitize()
        return share_config


class ShareInstanceService():
    def __init__(self) -> None:
        self.share_config_dao = ShareConfigDao()
        self.user_dao = UserDao()
        self.data_source_dao = DataSourceDao()
        self.display_schema_dao = DisplaySchemaDao()

    def get_by_id(self,
                  id: str,
                  password: str,
                  query: dict,
                  jwt_id: str):
        # get share_config by id
        share_config = self.share_config_dao.get_by_id(id)

        # check auth
        if share_config.password is not None:
            self.share_config_dao.assert_password_match(share_config, password)

        # get project
        project = share_config.linked_project

        # get first data_source
        # TODO: change to support multiple data sources
        data_sources = project.data_sources
        if len(data_sources) <= 0:
            raise InvalidParamError(
                'Project {} has no data sources.'.format(project.id))
        data_source = data_sources[0]

        # get latest data
        self.data_source_dao.refresh_data(data_source, query)

        # get display_schema
        display_schema = project.display_schema

        # TODO: assemble all above int ECharts option format

        # TODO: return option response
        return {}

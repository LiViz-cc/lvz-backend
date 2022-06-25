
from datetime import datetime
from typing import List
from dao import *
from models import *
from utils.common import *


logger = get_the_logger()


class ShareConfigService:
    def __init__(self) -> None:
        self.share_config_dao = ShareConfigDao()
        self.project_dao = ProjectDao()
        self.user_dao = UserDao()

    def get_share_configs(self, args, user) -> List[ShareConfig]:
        # TODO: accept query

        # validate args and construct query dict
        query = {}
        query['created_by'] = user

        # query projects with query dict
        share_configs = ShareConfig.objects(**query)

        # query set cannot be modified
        # create a new list for return
        share_configs_list = []

        for share_config in share_configs:
            share_config.desensitize()
            share_configs_list.append(share_config)

        logger.info("Query processed. Detail: {}".format(query))
        return share_configs_list

    def get_by_id(self, id: str, password: str) -> ShareConfig:
        # query project via id
        share_config = self.share_config_dao.get_by_id(id)

        # check if password-protected
        self.share_config_dao.assert_password_match(share_config, password)

        # remove password field for return
        share_config.desensitize()
        return share_config

    def create_share_config(self,
                            body: dict,
                            user: User,
                            project_id: str,
                            password_protected: bool,
                            password: str):
        project = self.project_dao.get_by_id(project_id)

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

        share_config.desensitize()
        return share_config

    def put_by_id(self, id: str, user, password: str, body: dict) -> ShareConfig:
        # query project via id
        share_config = self.share_config_dao.get_by_id(id)

        if share_config.created_by != user:
            raise ForbiddenError(
                "Cannot edit a share config not created by current user.")

        # check if password-protected
        self.share_config_dao.assert_password_match(share_config, password)

        # Forbid changing immutable field
        self.share_config_dao.assert_fields_editable(body)

        # update modified time
        body["modified"] = datetime.datetime.utcnow

        # update project
        self.share_config_dao.modify(share_config, body)

        share_config.desensitize()
        return share_config

    def delete_by_id(self, id: str, user, password: str) -> dict:
        # query project via id
        share_config = self.share_config_dao.get_by_id(id)

        if share_config.created_by != user:
            raise ForbiddenError()

        # check if password-protected
        self.share_config_dao.assert_password_match(share_config, password)

        # delete project
        share_config.delete()

        return {}

    def change_password(self, id: str, user, old_password: str, new_password: str) -> ShareConfig:
        # query project via id
        share_config = self.share_config_dao.get_by_id(id)

        if share_config.created_by != user:
            raise ForbiddenError()

        # check if password-protected
        self.share_config_dao.assert_password_match(share_config, old_password)

        myguard.check_literaly.password(new_password, is_new=True)

        modifing_dict = {'password': new_password,
                         'modified': datetime.datetime.utcnow}

        # save share config
        self.share_config_dao.modify(share_config, modifing_dict)

        share_config.desensitize()
        return share_config

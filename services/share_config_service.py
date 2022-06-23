
from asyncio.log import logger
from datetime import datetime
from typing import List

from errors import (ForbiddenError, InvalidParamError, NotFinishedYet,
                    NotFoundError, NotMutableError)
from models import Project, User
from models.ShareConfig import ShareConfig
from mongoengine.errors import DoesNotExist, ValidationError
from utils import get_current_user, get_the_logger, myguard
from utils.guard import myguard
from utils.logger import get_the_logger


logger = get_the_logger()


class ShareConfigService:
    def check_password_protected(self, share_config: ShareConfig, password: str) -> None:
        if share_config is None or not isinstance(share_config, ShareConfig):
            raise InvalidParamError(
                'Input "share_config" is None or not a type of ShareConfig.')

        if share_config.password_protected:
            # if password protected
            if not password:
                raise InvalidParamError(
                    "This share config is password-protected. Please provide password in the query.")

            myguard.check_literaly.password(password=password, is_new=False)
            if not share_config.check_password(password):
                raise ForbiddenError('Password is not correct.')
        # else:
        #     # if NOT password protected
        #     if password:
        #         raise InvalidParamError(
        #             "This share config is not password-protected. Do not provide password.")

    def _get_share_config_by_id(self, id) -> ShareConfig:
        myguard.check_literaly.object_id(id)

        # get share config from database
        try:
            share_config = ShareConfig.objects.get(id=id)
        except DoesNotExist:
            raise NotFoundError('share_configs', 'id={}'.format(id))
        return share_config

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
        share_config = self._get_share_config_by_id(id)

        # check if password-protected
        self.check_password_protected(share_config, password)

        # remove password field for return
        share_config.desensitize()
        return share_config

    def create_share_config(self, body: dict, user: User, project_name: str, password_protected: bool, password: str):
        myguard.check_literaly.object_id(
            project_name, object_name="linked_project")

        try:
            project = Project.objects.get(id=project_name)
        except DoesNotExist:
            raise NotFoundError('project', 'id={}'.format(project_name))

        if project.created_by != user:
            raise ForbiddenError(
                "Cannot share a project not created by current user.")

        # pre-validate params (password)

        if password_protected is None:
            raise InvalidParamError('"password_protected" should be provided.')

        if password_protected:
            myguard.check_literaly.password(password=password, is_new=True)
        else:
            if password is not None:
                raise InvalidParamError(
                    '"password" should not be provided when "password_protected" is disabled.')

        # construct new project object
        share_config = ShareConfig(**body)

        # set time
        curr_time = datetime.utcnow
        share_config.created = curr_time
        share_config.modified = curr_time

        # set created by
        share_config.created_by = user

        # save share config
        try:
            share_config.save()
        except ValidationError as e:
            raise InvalidParamError(e.message)

        # update user's and project's reference to share_config
        try:
            project.update(push__share_configs=share_config)
        except ValidationError as e:
            raise InvalidParamError(e.message)

        share_config.desensitize()
        return share_config

    def put_by_id(self, id: str, user, password: str, body: dict) -> ShareConfig:
        # query project via id
        share_config = self._get_share_config_by_id(id)

        if share_config.created_by != user:
            raise ForbiddenError(
                "Cannot edit a share config not created by current user.")

        # check if password-protected
        self.check_password_protected(share_config, password)

        # Forbid changing immutable field
        for field_name in ShareConfig.uneditable_fields:
            if body.get(field_name, None):
                raise NotMutableError(ShareConfig.__name__, field_name)

        # update modified time
        body["modified"] = datetime.utcnow

        # update project
        try:
            share_config.modify(**body)
        except ValidationError as e:
            raise InvalidParamError(e.message)
        except LookupError as e:
            raise InvalidParamError(e.message)

        share_config.desensitize()
        return share_config

    def delete_by_id(self, id: str, user, password: str) -> dict:
        # query project via id
        share_config = self._get_share_config_by_id(id)

        if share_config.created_by != user:
            raise ForbiddenError()

        # check if password-protected
        self.check_password_protected(share_config, password)

        # delete project
        share_config.delete()

        return {}

    def change_password(self, id: str, user, old_password: str, new_password: str) -> ShareConfig:
        # query project via id
        share_config = self._get_share_config_by_id(id)

        if share_config.created_by != user:
            raise ForbiddenError()

        # check if password-protected
        self.check_password_protected(share_config, old_password)

        myguard.check_literaly.password(new_password, is_new=True)
        share_config['password'] = new_password
        # share_config.hash_password()
        share_config['modified'] = datetime.utcnow

        # save share config
        try:
            share_config.save()
        except ValidationError as e:
            raise InvalidParamError(e.message)

        share_config.desensitize()
        return share_config

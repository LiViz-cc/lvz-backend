
from datetime import datetime

from errors import (ForbiddenError, InvalidParamError, NotFinishedYet,
                    NotFoundError, NotMutableError)

from models.ShareConfig import ShareConfig
from mongoengine.errors import DoesNotExist, ValidationError

from utils.guard import myguard


class ShareConfigCenter:
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
        else:
            # if NOT password protected
            if password:
                raise InvalidParamError(
                    "This share config is not password-protected. Do not provide password.")

    def get_with_id(self, id: str, password: str) -> ShareConfig:
        print(id)
        myguard.check_literaly.object_id(id)

        # get share config from database
        try:
            share_config = ShareConfig.objects.get(id=id)
        except DoesNotExist:
            raise NotFoundError('share_configs', 'id={}'.format(id))

        # check if password-protected
        self.check_password_protected(share_config, password)

        # remove password field for return
        share_config.desensitize()
        return share_config

    def put_with_id(self, id: str, user, password: str, body: dict) -> ShareConfig:
        # query project via id
        myguard.check_literaly.object_id(id)

        try:
            share_config = ShareConfig.objects.get(id=id)
        except DoesNotExist:
            raise NotFoundError('share_config', 'id={}'.format(id))

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

    def delete_with_id(self, id: str, user, password: str) -> dict:
        # query project via id
        myguard.check_literaly.object_id(id)

        try:
            share_config = ShareConfig.objects.get(id=id)
        except DoesNotExist:
            raise NotFoundError('share_config', 'id={}'.format(id))

        if share_config.created_by != user:
            raise ForbiddenError()

        # check if password-protected
        self.check_password_protected(share_config, password)

        # delete project
        share_config.delete()

        return {}

from errors import (EmailAlreadyExistsError, ForbiddenError, InvalidParamError,
                    NotFoundError, NotMutableError, UnauthorizedError)
from models import DataSource, DisplaySchema, Project, ShareConfig, User
from mongoengine.errors import DoesNotExist, NotUniqueError, ValidationError
from utils.guard import myguard


class ShareConfigDao:
    def check_password(self, share_config: ShareConfig, password: str) -> bool:
        myguard.check_literaly.password(password=password, is_new=False)
        return share_config.password == password

    def assert_password_match(self, share_config: ShareConfig, password: str) -> None:
        if share_config is None or not isinstance(share_config, ShareConfig):
            raise InvalidParamError(
                'Input "share_config" is None or not a type of ShareConfig.')

        if not password:
            raise InvalidParamError(
                "This share config is password-protected. Please provide password in the JSON body.")

        if not self.check_password(share_config, password):
            raise ForbiddenError('Password is not correct.')

    def desensitize(self, share_config: ShareConfig):
        if hasattr(share_config, 'password'):
            del share_config.password

    def get_by_id(self, id: str) -> ShareConfig:
        myguard.check_literaly.object_id(id)

        # get share config from database
        try:
            share_config = ShareConfig.objects.get(id=id)
        except DoesNotExist:
            raise NotFoundError('share_configs', 'id={}'.format(id))
        return share_config

    def save(self, share_config: ShareConfig, *args, **kwargs) -> None:
        try:
            share_config.save(*args, **kwargs)
        except ValidationError as e:
            raise InvalidParamError(e.message)

    def modify(self, share_config: ShareConfig, body: dict) -> None:
        try:
            share_config.modify(**body)
        except ValidationError as e:
            raise InvalidParamError(e.message)
        except LookupError as e:
            raise InvalidParamError(e.message)

    def assert_fields_editable(self, body: dict) -> None:
        for field_name in ShareConfig.uneditable_fields:
            if body.get(field_name, None):
                raise NotMutableError(ShareConfig.__name__, field_name)

from models import ShareConfig
from utils.common import *


class ShareConfigDao:
    def save(self, share_config: ShareConfig):
        try:
            share_config.save()
        except ValidationError as e:
            raise InvalidParamError(e.message)

    # TODO: CHANGE TO PLAIN TEXT
    def check_password(self, share_config: ShareConfig, password):
        return share_config.password == password

    def desensitize(self, share_config: ShareConfig):
        if hasattr(share_config, 'password'):
            del share_config.password

from models import ShareConfig


from utils.common import *


class ShareConfigDao:
    def save(self, share_config: ShareConfig):
        try:
            share_config.save()
        except ValidationError as e:
            raise InvalidParamError(e.message)


from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from errors import InvalidParamError
from utils.guard import myguard
from utils.logger import get_the_logger
from services import ShareInstanceService

from .response_wrapper import response_wrapper
import utils


class ShareInstanceResource(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.share_instance_service = ShareInstanceService()

    @response_wrapper
    @jwt_required(optional=True)
    def get(self, id):
        myguard._check.object_id(id)
        query = dict(request.args)
        jwt_id = get_jwt_identity()
        password = query.get('_pw')

        utils.myguard.check_literaly.check_type([
            (str, id, 'id', True),
            (str, password, '_pw', False)
        ])

        utils.logger.info(
            'GET share instance with id {}, jwt_id {}, password {} and query {}'.format(id, jwt_id, password, query))

        return self.share_instance_service.get_by_id(id, password, query, jwt_id)

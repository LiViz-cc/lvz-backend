from flask_restful import Resource
from .response_wrapper import response_wrapper

ROOT_INFO = {
    'title': 'REST API of LiViz',
    'github': 'https://github.com/LiViz-cc/lvz-backend'
}

class RootResource(Resource):
    def __init__(self) -> None:
        super().__init__()

    @response_wrapper
    def get(self):
        return ROOT_INFO

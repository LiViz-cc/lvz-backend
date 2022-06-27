import json

from errors import ServerError
from flask import Response
from flask_jwt_extended.exceptions import NoAuthorizationError
import traceback
from utils import get_the_logger
logger = get_the_logger()


def response_wrapper(func):
    # # ref: https://stackoverflow.com/a/48457726/11071084
    # def to_dict(obj):
    #     if isinstance(obj, (QuerySet, list)):
    #         return list(map(to_dict, obj))
    #     elif isinstance(obj, (Document, EmbeddedDocument)):
    #         doc = {}
    #         for field_name in obj._fields.keys():
    #             print(field_name)
    #             field_value = getattr(obj, field_name)
    #             doc[field_name] = to_dict(field_value)
    #         return doc
    #     else:
    #         return obj

    # class MongoJsonEncoder(json.JSONEncoder):
    #     def default(self, obj):
    #         if isinstance(obj, bson.ObjectId):
    #             return str(obj)
    #         if isinstance(obj, bson.DBRef):
    #             return str(obj.id)
    #         return json.JSONEncoder.default(self, obj)

    def wrapper(*args, **kwargs):
        try:
            # get response
            response = func(*args, **kwargs)
            response_json: str

            if type(response) == dict:
                response_json = json.dumps(response)

            elif type(response) == list:
                # TODO: refine the convertion from List of Document to JSON
                response_json_list = (x.to_json() for x in response)
                response_json = '[' + ','.join(response_json_list) + ']'

            else:
                response_json = response.to_json()

            return Response(response_json, mimetype='application/json', status=200)
        except NoAuthorizationError as e:
            # wrap jwt authorization error
            return {'title': 'Forbidden', 'status': 403, 'detail': 'Cannot access with given authorization.'}, 403
        except ServerError as e:
            # wrap server error with given status and error title, detail
            return {'title': e.title, 'status': e.status, 'detail': e.detail}, e.status
        except Exception as e:
            # wrap other exceptions with status 500
            return {'title': 'Internal Server Error', 'status': 500, 'detail': str(e)}, 500
    return wrapper

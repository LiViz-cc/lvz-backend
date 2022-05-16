from flask import Response
from mongoengine import Document, EmbeddedDocument, QuerySet
from flask_jwt_extended.exceptions import NoAuthorizationError
from errors import ServerError
import json, bson


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

            if type(response) == dict:
                # wrap simple dict response
                return Response(json.dumps(response), mimetype='application/json', status=200)

            # got Document or Document List (QuerySet)
            # # first convert to dict
            # response_dict = to_dict(response)
            # # then dump to json string
            # response_json = json.dumps(response_dict, cls=MongoJsonEncoder)
            # # finally wrap json string response
            # return Response(response_json, mimetype='application/json', status=200)
            return Response(response.to_json(), mimetype='application/json', status=200)
        except NoAuthorizationError as e:
            # wrap jwt authorization error
            return {'title': 'Forbidden', 'status': 403, 'detail': 'Cannot access with given authorization.'}, 403
        except ServerError as e:
            # wrap server error with given status and error title, detail
            return {'title': e.title, 'status': e.status, 'detail': e.detail}, e.status
        except Exception as e:
            print(e)
            # wrap other exceptions with status 500
            return {'title': 'Internal Server Error', 'status': 500, 'detail': str(e)}, 500
    return wrapper

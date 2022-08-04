

from errors import InvalidParamError
from .guard import myguard


def convert_string_to_bool(param: str, param_name: str) -> bool:
    myguard.check_literaly.check_type([
        (str, param, 'param', False),
        (str, param_name, 'param_name', False)
    ])

    param_bool = None

    if param.lower() == 'true':
        param_bool = True
    elif param.lower() == 'false':
        param_bool = False
    else:
        raise InvalidParamError('"{}" must be a boolean.'.format(param_name))

    return param_bool

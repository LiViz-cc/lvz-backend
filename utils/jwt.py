from errors import (ForbiddenError, InvalidParamError, NotFinishedYet,
                    NotFoundError, NotMutableError)
from flask_jwt_extended import get_jwt_identity
from models import User
from mongoengine.errors import DoesNotExist

from .guard import myguard


def get_current_user() -> User:
    # check authorization
    user_id = get_jwt_identity()
    myguard.check_literaly.user_id(user_id)

    try:
        user = User.objects.get(id=user_id)
    except DoesNotExist:
        raise NotFoundError('user', 'id={}'.format(user_id))

    return user

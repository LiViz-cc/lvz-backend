import datetime
import json
from dataclasses import fields

from database import db
from errors import (EmailAlreadyExistsError, ForbiddenError, InvalidParamError,
                    NotFoundError, NotMutableError, UnauthorizedError)
from flask import request
from flask_bcrypt import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token
from flask_restful import Resource
from mongoengine.errors import DoesNotExist, NotUniqueError, ValidationError
from mongoengine.fields import (DateTimeField, EmailField, ListField,
                                ReferenceField, StringField)

from utils.guard import myguard
from utils.logger import get_the_logger

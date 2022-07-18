
import datetime
import hashlib
import json

from dao import (DataSourceDao, DisplaySchemaDao, ProjectDao, ShareConfigDao,
                 UserDao, data_source_dao)
from errors import (EmailAlreadyExistsError, ForbiddenError, InvalidParamError,
                    NotFoundError, NotMutableError, UnauthorizedError)
from flask_jwt_extended import create_access_token
from models import DataSource, DisplaySchema, Project, ShareConfig, User
import utils
from utils.guard import myguard
from utils.logger import get_the_logger

logger = get_the_logger()


class UserService():
    def __init__(self) -> None:
        self.user_dao = UserDao()
        self.project_dao = ProjectDao()
        self.data_source_dao = DataSourceDao()

    def get_user_by_id(self, id, jwt_id) -> User:
        # check authorization
        myguard.check_literaly.user_id(jwt_id)

        # query user via id
        user = self.user_dao.get_user_by_id(id)

        # user can only get their own info
        if jwt_id != str(user.id):
            raise ForbiddenError()

        return user

    def change_password(self, id, jwt_id, old_password, new_password):
        # pre-validate params
        myguard.check_literaly.password(
            old_password, is_new=False, password_alies='old_password')

        myguard.check_literaly.password(
            new_password, is_new=True, password_alies='new_password')

        # get user from database
        user = self.user_dao.get_user_by_id_with_sensitive_info(id)

        # check authorization
        myguard.check_literaly.user_id(jwt_id)
        if id != jwt_id:
            raise ForbiddenError()

        # check if old_password is as same as the password in the database
        self.user_dao.assert_password_match(user, old_password)

        # Forbid changing immutable field
        modifing_dict = {}
        # add password into dict
        modifing_dict['password'] = self.user_dao.get_password_hash(
            new_password)
        modifing_dict['modified'] = datetime.datetime.utcnow

        # update project
        self.user_dao.modify(user, modifing_dict)

        user.desensitize()
        return user

    def signUp(self, email: str, password: str, username: str, *args, **kwargs):
        if not username:
            username = hashlib.sha256(email.encode('UTF-8')).hexdigest()[:10]
            # TODO: check if hash crashed. If so, add one more round

        # TODO: add check if username already in

        # Pack body
        body = {'email': email, 'password': password, 'username': username}

        # construct new user object
        user = User(**body)

        # set time
        curr_time = utils.get_utcnow()
        user.created = curr_time
        user.modified = curr_time

        # hash passord
        # must manually call this function before save
        self.user_dao.hash_password(user)

        # save new user
        self.user_dao.save(user)

        # return desensitized created user
        self.user_dao.desensitize(user)
        logger.info("Created a user with email {}".format(body.get('email')))
        return user

    def login(self, email: str, password: str, username: str):
        # pre-validate params
        myguard.check_literaly.password(password=password, is_new=False)

        # query user
        if email is not None:
            user = self.user_dao.get_user_by_email_with_sensitive_info(email)
        elif username is not None:
            user = self.user_dao.get_user_by_username(
                username, desensitized=False)
        else:
            raise InvalidParamError('Please provide either username or email.')

        # check password
        self.user_dao.assert_password_match(user, password)

        # create access token
        expires = datetime.timedelta(days=7)
        access_token = create_access_token(
            identity=str(user.id), expires_delta=expires)

        # return desensitized created user
        user.desensitize()
        return {'token': access_token, 'user': json.loads(user.to_json())}

    def reset_by_id(self, id: str, password: str, jwt_id: str):
        # NOTE: Danger! This method is only allowed in development mode

        # check auth
        if id != jwt_id:
            raise ForbiddenError()

        # get user
        user = self.user_dao.get_user_by_id_with_sensitive_info(id)

        # check password
        self.user_dao.assert_password_match(user, password)

        print('here')

        for project in user.projects:
            self.project_dao.delete(project)

        for data_source in user.data_sources:
            self.data_source_dao.delete(data_source)

        user = self.user_dao.get_user_by_id(id)

        user.desensitize()
        return user

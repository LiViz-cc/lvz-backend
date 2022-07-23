
import datetime
import json
import os
from typing import List
from urllib import response

import requests

import utils
from dao import (DataSourceDao, DisplaySchemaDao, ProjectDao, ShareConfigDao,
                 UserDao)
from dotenv import load_dotenv
from errors import (EmailAlreadyExistsError, ForbiddenError, InvalidParamError,
                    NotFoundError, NotMutableError, UnauthorizedError)
from flask import Response
from models import DataSource, DisplaySchema, Project, ShareConfig, User
from mongoengine.errors import DoesNotExist, NotUniqueError, ValidationError
from utils.guard import myguard


class ApiFetchService:
    def __init__(self) -> None:
        self.user_dao = UserDao()
        self.project_dao = ProjectDao()
        self.data_source_dao = DataSourceDao()
        self.display_schema_dao = DisplaySchemaDao()
        self.weather_api = WeatherAPI()

    def get_data(self, url, slots: List[dict], query: dict) -> dict:
        request_params = {}

        for slot in slots:
            name, type, optional, default, alias = [
                slot.get(x) for x in ['name', 'slot_type', 'optional', 'default', 'alias']]

            utils.myguard.check_literaly.check_type([
                (str, name, 'name', False),
                (str, type, 'slot_type', False),
                (bool, optional, 'optional', True),
                (str, default, 'default', True),
                (str, alias, 'alias', True),
            ])

            param_name = alias if alias else name
            if param_name in request_params:
                raise InvalidParamError(
                    'Slot "{}" contains duplicate param names or aliases.'.format(name))

            if not optional:
                # field is required
                if param_name not in query:
                    raise InvalidParamError(
                        'Please provide {} in query.'.format(name))

                request_params[name] = query[param_name]
            else:
                # field is optional
                if param_name in query:
                    request_params[name] = query[param_name]
                elif default:
                    request_params[name] = default

        response = requests.get(url=url, params=request_params)
        return json.loads(response.text)

        if 'api.weatherapi.com' in url:
            return self.weather_api.get_data_for_one(query=query)


class WeatherAPI():
    def __init__(self) -> None:
        # load_dotenv()
        # self.weather_api_key = os.getenv('WEATHER_API_KEY')
        # self.url = 'https://api.weatherapi.com/v1/current.json'.format(
        #     self.weather_api_key)
        pass

    @classmethod
    def check_status_code(cls, response: Response):
        if response.status_code != 200:
            # raise Exception
            print('status_code: {}'.format(response.status_code))
            pass

    def get_data_for_one(self, query: dict = {}) -> dict:
        response = requests.get(url=self.url, params=query)
        # WeatherAPI.check_status_code(response)
        return json.loads(response.text)

    def get_data(self, queries: dict = {}) -> dict:
        ret = {}
        for idx, query in queries.items():
            ret[idx] = self.get_data_for_one(query=query)
        return ret

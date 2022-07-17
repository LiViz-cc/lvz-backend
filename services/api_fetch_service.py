
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
        available_params = set()
        for slot in slots:
            name = slot.get('name')
            if name is None:
                raise InvalidParamError(
                    '"name" attribute is missing in a slot in data_source')

            if name in available_params:
                raise InvalidParamError('Detect duplicate names of slots')

            available_params.add(name)

        request_params = {}
        for k, v in query.items():
            if k not in available_params:
                raise InvalidParamError(
                    '{} is not allowed in this data source'.format(k))

            request_params[k] = v

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

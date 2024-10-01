import logging
from abc import abstractmethod

import requests

from flaskd3.infrastructure.external_clients import constants
from flaskd3.infrastructure.external_clients.base_response_object import (
    BaseResponseObject,
)

logger = logging.getLogger(constants.EXTERNAL_CLIENTS_LOGGER_PREFIX + __name__)


class BaseExternalClient(object):
    """
    BaseExternalClient
    """

    page_map = dict()

    def __init__(self, timeout=30, log_handler=None):
        self.logger = logger or log_handler
        self.timeout = timeout

    class CallTypes(object):
        """
        CallTypes
        """

        POST = "post"
        GET = "get"
        PUT = "put"
        DELETE = "delete"

        call_mapper = {
            GET: requests.get,
            POST: requests.post,
            PUT: requests.put,
            DELETE: requests.delete,
        }

        @classmethod
        def get_request(cls, call_type):
            """
            :param call_type:
            :return:
            """
            return cls.call_mapper.get(call_type)

    def get_page_map(self):
        """
        returns the pagename -> url map for the external api's
        Returns:

        """
        return self.page_map

    @abstractmethod
    def get_domain(self):
        """
        The domain of the external service being called. Need to be implemented by each client.
        :return: Domain of the external system
        """
        pass

    def get_api(self, page_name, **kwargs):
        ret_val = dict(self.get_page_map()[page_name])
        ret_val["url"] = ret_val["url_regex"].format(**kwargs)
        return ret_val

    def make_call(self, page_name, data=None, url_parameters=None, custom_headers=None):
        """
        API to make the external call
        :param data:
        :param page_name:
        :param url_parameters:
        :param custom_headers:
        :return:
        """
        if not url_parameters:
            url_parameters = dict()
        api = self.get_api(page_name, **url_parameters)
        api_type = api.get("type")
        url = self.get_domain() + api.get("url")

        headers = {"referrer": "/", "content-type": "application/json"}

        if custom_headers:
            headers.update(custom_headers)

        logger.info(
            "%s:: Making call %s to url: %s with headers: %s and payload: %s",
            self.__class__.__name__,
            api_type,
            url,
            headers,
            data,
        )

        try:
            request_params = dict(url=url, headers=headers, allow_redirects=True, timeout=self.timeout)

            if api_type == self.CallTypes.GET:
                request_params["params"] = data

            else:
                request_params["json"] = data

            response = self.CallTypes.get_request(api_type)(**request_params)
            response_object = BaseResponseObject(response)
            logger.info("%s:: response: %s", self.__class__.__name__, response_object)

        except Exception as e:
            logger.exception("BaseExternalClient Exception")
            return BaseResponseObject(None)

        return response_object

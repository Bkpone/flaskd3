import requests


class BaseResponseObject(object):
    def __init__(self, response):
        self.response_code = 500
        self.data = None
        self.errors = dict()
        self.json_response = dict()
        self.response = response
        # TODO:: Handle other content-types
        if response is not None:
            if response.headers.get("content-type") and "application/json" in response.headers.get("content-type"):
                self.json_response = response.json()
                if isinstance(self.json_response, dict):
                    self.data = self.json_response.get("data", self.json_response)
                    self.errors = self.json_response.get("errors")
            else:
                self.data = dict(text=self.response.text)
            self.response_code = response.status_code
        if not self.is_success():
            self.errors = self.json_response.get("errors") if self.json_response.get("errors") else self.json_response

    def is_success(self):
        """
        Is the response successful or not
        :return: success if response code is 200 or 201
        """
        if not self.response_code:
            return False

        ret_val = self.response_code in [requests.codes.ok, requests.codes.created]

        return ret_val

    @property
    def status_code(self):
        return self.response_code

    def __str__(self):
        return "status_code: {} data: {} errors: {}".format(self.status_code, self.data, self.errors)

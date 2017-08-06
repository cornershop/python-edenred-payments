# encoding=UTF-8
from __future__ import unicode_literals


class APIError(Exception):

    def __init__(self, response, description):
        super(APIError, self).__init__(response.status_code, description)
        self.response = response
        self.description = description

    @property
    def status_code(self):
        return self.response.status_code

    @staticmethod
    def create_from_http_error(error):
        if error.response.status_code == 403:
            return Unauthorized(error.response)
        if error.response.status_code == 401:
            return InvalidCredentials(error.response)
        return APIError(error.response, error.response.reason)


class InvalidCredentials(APIError):
    def __init__(self, response):
        super(InvalidCredentials, self).__init__(response, "Invalid Credentials")


class Unauthorized(APIError):
    def __init__(self, response):
        super(Unauthorized, self).__init__(response, "Unauthorized")


class TransactionErrors(Exception):

    def __init__(self, response, errors):
        error_message = self.extract_error_message(errors)
        super(TransactionErrors, self).__init__(error_message, *[error['Code'] for error in errors])
        self.errors = errors
        self.response = response

    @classmethod
    def extract_error_message(cls, errors):
        sorted_errors = sorted(errors, key=lambda error: error['Code'])
        return sorted_errors[0]['Message'] if len(sorted_errors) > 0 else "Error desconocido"

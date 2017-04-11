

class APIError(Exception):
    ERROR_CODE = None
    ERROR_MESSAGE = 'API Error'

    def __init__(self, http_error):
        super(APIError, self).__init__(self.ERROR_MESSAGE)
        self.http_error = http_error

    def get_error_message(self):
        meta = self.http_error.response.json()['meta']
        for message in meta['messages']:
            if message['code'] == self.ERROR_CODE:
                return message['message']
        return meta['status']

    @staticmethod
    def create_from_http_error(error):
        if error.response.status_code == Unauthorized.status_code:
            return Unauthorized(error)
        return APIError(error)


class Unauthorized(APIError):
    status_code = 401

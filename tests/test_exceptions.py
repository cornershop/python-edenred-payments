import unittest

try:
    from unitttest import mock
except ImportError:
    import mock

from edenred.exceptions import APIError, InvalidCredentials, Unauthorized


class TestCreateAPIError(unittest.TestCase):
    def assert_error(self, error, response, description, cls=APIError):
        self.assertIsInstance(error, cls)
        self.assertEqual(response, error.response)
        self.assertEqual(description, error.description)

    def setUp(self):
        self.response = mock.Mock()
        self.http_error = mock.Mock()
        self.http_error.response = self.response

    def test_init(self):
        description = mock.Mock()
        error = APIError(self.response, description)

        self.assertEqual(self.response, error.response)
        self.assertEqual(description, error.description)
        self.assertEqual(self.response.status_code, error.status_code)

    def test_create_from_403(self):
        self.response.status_code = 403

        error = APIError.create_from_http_error(self.http_error)

        self.assert_error(error, self.response, 'Unauthorized', Unauthorized)

    def test_create_from_401(self):
        self.response.status_code = 401

        error = APIError.create_from_http_error(self.http_error)

        self.assert_error(error, self.response, 'Invalid Credentials', InvalidCredentials)

    def test_create_from_xxx(self):
        error = APIError.create_from_http_error(self.http_error)

        self.assert_error(error, self.response, self.response.reason)

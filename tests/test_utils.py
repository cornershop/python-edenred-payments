
from unittest import TestCase
try:
    from unitttest import mock
except ImportError:
    import mock

from edenred.utils import PublicKey


class TestPublicKey(TestCase):
    def test_init(self):
        path = mock.Mock(spec=str)
        key = PublicKey(path)

        self.assertEqual(path, key.path)
        self.assertFalse(key.testing)

    def test_init_testing(self):
        path = mock.Mock(spec=str)
        testing = mock.Mock(spec=bool)
        key = PublicKey(path, testing)

        self.assertEqual(path, key.path)
        self.assertEqual(testing, key.testing)

    def test_encrypt_testing(self):
        path = mock.Mock(spec=str)
        key = PublicKey(path)

        data = mock.Mock(spec=str)

        self.assertEqual(data, key.encrypt(data))

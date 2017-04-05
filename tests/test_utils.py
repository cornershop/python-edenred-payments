
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

    def test_encrypt(self):
        path = mock.Mock(spec=str)
        key = PublicKey(path)

        data = mock.Mock(spec=str)

        self.assertEqual(data, key.encrypt(data))

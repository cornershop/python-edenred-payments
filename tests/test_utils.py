
import os
import random
from base64 import b64encode
from unittest import TestCase
try:
    from unitttest import mock
except ImportError:
    import mock

from Crypto.PublicKey import RSA

from edenred.utils import PublicKey

KEYS_DIR = os.path.join(os.path.dirname(__file__), "keys")


class TestPublicKey(TestCase):
    def get_random_length(self):
        return random.choice((1024, 2048, 3072, 4096))

    def get_key_path(self, length):
        return os.path.join(KEYS_DIR, "{}.pub".format(length))

    def get_public_key(self, length):
        key_path = self.get_key_path(length)
        with open(key_path, 'r') as key_file:
            return RSA.importKey(key_file.read())

    def test_init(self):
        length = self.get_random_length()
        path = self.get_key_path(length)
        key = PublicKey(path)

        expected = self.get_public_key(length)

        self.assertEqual(expected, key.rsa)
        self.assertFalse(key.testing)

    def test_init_testing(self):
        length = self.get_random_length()
        path = self.get_key_path(length)
        testing = mock.Mock(spec=bool)
        expected = self.get_public_key(length)

        key = PublicKey(path, testing)

        self.assertEqual(expected, key.rsa)
        self.assertEqual(testing, key.testing)

    def test_encrypt_testing(self):
        length = self.get_random_length()
        path = self.get_key_path(length)
        key = PublicKey(path, testing=True)

        data = mock.Mock(spec=str)

        self.assertEqual(data, key.encrypt(data))

    def test_encrypt(self):
        length = self.get_random_length()
        path = self.get_key_path(length)
        rsa = self.get_public_key(length)
        message = "123456789abcdefghij"
        encrypted = rsa.encrypt(message, None)[0]
        expected = b64encode(encrypted)

        key = PublicKey(path)

        self.assertEqual(expected, key.encrypt(message))

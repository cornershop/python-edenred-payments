
import os
import tempfile
import base64
from unittest import TestCase
try:
    from unitttest import mock
except ImportError:
    import mock

import Crypto.PublicKey.RSA
import Crypto.Cipher.PKCS1_v1_5

from edenred.utils import PublicKey


class TestPublicKey(TestCase):
    def __init__(self, *args, **kwargs):
        self.length = 1024
        self.private = Crypto.PublicKey.RSA.generate(self.length)
        self.public = self.private.publickey()
        super(TestPublicKey, self).__init__(*args, **kwargs)

    def setUp(self):
        _, self.private_path = tempfile.mkstemp(suffix='.pem', prefix='private-')
        with open(self.private_path, 'w') as private_key_file:
            private_key_file.write(self.private.exportKey('PEM'))

        _, self.public_path = tempfile.mkstemp(suffix='.pem', prefix='public-')
        with open(self.public_path, 'w') as public_key_file:
            public_key_file.write(self.public.exportKey('PEM'))

    def tearDown(self):
        os.unlink(self.private_path)
        os.unlink(self.public_path)

    def assert_pkcs1_encrypted(self, message, encrypted, private_key=None):
        private_key = self.private if private_key is None else private_key
        encrypted = base64.b64decode(encrypted.encode())
        cipher = Crypto.Cipher.PKCS1_v1_5.new(private_key)
        sentinel = Crypto.Random.new().read(len(message))

        decrypted = cipher.decrypt(encrypted, sentinel)

        self.assertEqual(message, decrypted)

    def test_init(self):
        key = PublicKey(self.public_path)

        self.assertEqual(self.public, key.rsa)
        self.assertFalse(key.testing)

    def test_init_testing(self):
        testing = mock.Mock(spec=bool)

        key = PublicKey(self.public_path, testing)

        self.assertEqual(self.public, key.rsa)
        self.assertEqual(testing, key.testing)

    def test_encrypt_testing(self):
        key = PublicKey(self.public_path, testing=True)

        data = mock.Mock(spec=str)

        self.assertEqual(data, key.encrypt(data))

    def test_encrypt(self):
        key = PublicKey(self.public_path)
        message = "123456789abcdefghij"

        encrypted = key.encrypt(message)

        self.assert_pkcs1_encrypted(message, encrypted)

    def test_equal(self):
        testing = mock.Mock(spec=bool)
        key1 = PublicKey(self.public_path, testing)
        key2 = PublicKey(self.public_path, testing)

        self.assertEqual(key1, key2)

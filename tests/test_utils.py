
import os
import tempfile
import base64
import unittest
try:
    from unitttest import mock
except ImportError:
    import mock

import Crypto.PublicKey.RSA
import Crypto.Cipher.PKCS1_v1_5

from edenred.utils import PublicKey

PRIVATE_KEY = """\
-----BEGIN RSA PRIVATE KEY-----
MIICXgIBAAKBgQDSQJ8lQtJMFxEdU8fx9kehxD2ONQwWXdNArKBzDJE5bF03T2QB
mivGXu71KWf7sO22IPZwv5yQlVWE9csJb2Muphpm7khg1qVactVluSkMgBIpATn4
F4VHtWmR0HNTIjy108BdFUYQaz3Cnla0KqDOevQtdCX7ndFvbsc8YQeclwIDAQAB
AoGAdWYj9vhS2K3gnpGTiaXM5aTgAjHYp/yH4wsBJHyV8oxxmFq6KrLdUozbvQT7
zOxEL3hEYzx6vbjE4dMlJgWOSRCSvyCwd9i/3OD0t3YRpXBjwxqmj7R5UROCljCL
R1Z+xafy6e1VMEycdjDtWYDdeFyvTq2pfsZNqgBxgoW34kECQQDdYUCboiND7Ao3
KAlivIxb/x+YssMWogbFMpl03J3OKhGqlCbYNbbz6hwWtvtA5OYiRdPeWQPuLbCb
OnWA56exAkEA8yHkIjbPPiJVz1hKT6wYQTlVrB9uPCJNSXQ5+CfiL7HKvnTiRk3p
/5HAp+tQjMhWXANobFfQlOYpCLhzfgrixwJBAK34dTtZCXmhDs4VinqrTWombYAk
SyeIIOXrQ6kQjnqrmMKCNpyGacX43iYDmiN/PlMEqOD89xe/lCAIqrqoUaECQQCd
GOb5nISoVzMu+JN7i21Yp51NzDlELb3WmnzidZLW0oB4M7oJR0rNUfY0Cf5QGRqD
9cfBSbSCoX0eH2CwroP9AkEA1kVSoOXRVti78SQG7HXvQdH4uOlHkj0A/1Yh1XqF
UFBSmgj49gZBKdKi67mLFG8Tlw02ufmUoEYPw8pmIj9obw==
-----END RSA PRIVATE KEY-----
"""


class TestPublicKey(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        self.private = Crypto.PublicKey.RSA.importKey(PRIVATE_KEY)
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

    def assert_pkcs1_b64_encrypted(self, message, encrypted):
        encrypted = base64.b64decode(encrypted.encode())
        cipher = Crypto.Cipher.PKCS1_v1_5.new(self.private)
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

        self.assert_pkcs1_b64_encrypted(message, encrypted)

    def test_equal(self):
        testing = mock.Mock(spec=bool)
        key1 = PublicKey(self.public_path, testing)
        key2 = PublicKey(self.public_path, testing)

        self.assertEqual(key1, key2)

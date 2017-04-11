
from base64 import b64encode

from Crypto.PublicKey import RSA


class PublicKey(object):
    def __init__(self, path, testing=False):
        self.path = path
        self.testing = testing
        with open(path, 'r') as key_file:
            self.rsa = RSA.importKey(key_file.read())

    def encrypt(self, data):
        if self.testing:
            return data
        encrypted = self.rsa.encrypt(data, None)[0]
        return b64encode(encrypted)

    def __eq__(self, other):
        return self.rsa == other.rsa and self.testing == other.testing


import base64


class PublicKey(object):
    def __init__(self, path, testing=False):
        self.path = path
        self.testing = testing
        self.rsa = self._import_rsa(path)

    @staticmethod
    def _import_rsa(path):
        import Crypto.PublicKey.RSA

        with open(path, 'r') as key_file:
            return Crypto.PublicKey.RSA.importKey(key_file.read())

    def encrypt(self, data):
        if self.testing:
            return data
        encrypted = self.cipher.encrypt(data.encode())
        return base64.b64encode(encrypted).decode()

    @property
    def cipher(self):
        return self._cipher

    @property
    def rsa(self):
        return self._rsa

    @rsa.setter
    def rsa(self, rsa):
        import Crypto.Cipher.PKCS1_v1_5
        self._rsa = rsa
        self._cipher = Crypto.Cipher.PKCS1_v1_5.new(rsa)

    def __eq__(self, other):
        return self.rsa == other.rsa and self.testing == other.testing

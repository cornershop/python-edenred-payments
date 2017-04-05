

class PublicKey(object):
    def __init__(self, path):
        self.path = path

    def encrypt(self, data):
        return data

    def __eq__(self, other):
        return self.path == other.path

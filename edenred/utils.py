

class PublicKey(object):
    def __init__(self, path, testing=False):
        self.path = path
        self.testing = testing

    def encrypt(self, data):
        if self.testing:
            return data
        return data

    def __eq__(self, other):
        return self.path == other.path and self.testing == other.testing

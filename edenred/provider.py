

class APIProviderBase(object):
    def __init__(self, public_key, access_token):
        self.public_key = public_key
        self.access_token = access_token

    @staticmethod
    def create_for_client(client_id, client_secret, public_key_path):
        public_key = APIProviderBase.get_public_key(public_key_path)
        access_token = APIProviderBase.create_access_token(client_id, client_secret, public_key)
        return APIProviderBase(public_key, access_token)

    @staticmethod
    def get_public_key(public_key_path):
        raise NotImplementedError()

    @staticmethod
    def create_access_token(client_id, client_secret, public_key):
        raise NotImplementedError()

    def authorize(self, card_token, amount, description):
        raise NotImplementedError()

    def pay(self, card_token, amount, description):
        raise NotImplementedError()

    def capture(self, card_token, authorize_identifier, amount):
        raise NotImplementedError()

    def create_payment_method(self, card_number, cvv, expiration_month, expiration_year, username, user_id):
        raise NotImplementedError()


class APIProvider(APIProviderBase):
    pass

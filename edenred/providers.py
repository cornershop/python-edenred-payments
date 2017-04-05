
import requests

from .utils import PublicKey


class APIProvider(object):
    def __init__(self, public_key, access_token, testing=False):
        self.public_key = public_key
        self.access_token = access_token
        self.testing = testing

    @staticmethod
    def create_for_client(client_id, client_secret, public_key_path, testing=False):
        public_key = APIProvider.get_public_key(public_key_path)
        access_token = APIProvider.create_access_token(client_id, client_secret, public_key, testing)
        return APIProvider(public_key, access_token)

    @staticmethod
    def get_public_key(public_key_path):
        return PublicKey(public_key_path)

    @staticmethod
    def create_access_token(client_id, client_secret, public_key, testing=False):
        login_url = APIProvider.get_endpoint_url('Login', testing=testing)
        payload = {
            "Security": {
                "ClientIdentifier": client_id,
                "ClientSecret": client_secret
            }
        }
        response = APIProvider.do_request(url=login_url, payload=payload, headers={})
        return response['access_token']

    @staticmethod
    def get_base_url(testing=False):
        return 'https://example.net'

    @staticmethod
    def get_endpoint_url(resource, testing=False):
        return "{}/{}".format(APIProvider.get_base_url(testing), resource)

    @staticmethod
    def do_request(url, headers, payload):
        response = requests.post(
            url,
            data=payload,
            headers=headers
        )
        return response.json()

    def authorize(self, card_token, amount, description):
        payload = {
            "Authorize": {
                "CardToken": card_token,
                "Amount": amount,
                "Description": description,
                "AuthorizeIdentifier": None
            }
        }
        data = self.request_resource('Authorize', payload)
        return data['Authorize']

    def pay(self, card_token, amount, description):
        payload = {
            "Pay": {
                "CardToken": card_token,
                "Amount": amount,
                "Description": description,
                "PayIdentifier": None
            }
        }
        data = self.request_resource('Pay', payload)
        return data['Pay']

    def capture(self, card_token, authorize_identifier, amount, description):
        payload = {
            "Capture": {
                "CardToken": card_token,
                "Amount": amount,
                "Description": description,
                "AuthorizeIdentifier": authorize_identifier,
                "CaptureIdentifier": None
            }
        }
        data = self.request_resource('Capture', payload)
        return data['Capture']

    def create_payment_method(self, card_number, cvv, expiration_month, expiration_year, username, user_id):
        payload = {
            "PaymentMethod": {
                "CardNumber": self.public_key.encrypt(card_number),
                "CardCVV": self.public_key.encrypt(cvv),
                "CardExpirationMonth": self.public_key.encrypt(expiration_month),
                "CardExpirationYear": self.public_key.encrypt(expiration_year),
                "UserLogin": username,
                "UserIdentifier": user_id,
                "CardToken": None
            }
        }
        data = self.request_resource('CreatePaymentMethod', payload)
        return data['PaymentMethod']

    def request_resource(self, resource, payload):
        return self.do_request(
            url=self.get_endpoint_url(resource=resource, testing=self.testing),
            headers=self._get_headers(),
            payload=payload
        )

    def _get_headers(self):
        return {'access_token': self.access_token}

    def __eq__(self, other):
        return self.public_key == other.public_key and self.access_token == other.access_token

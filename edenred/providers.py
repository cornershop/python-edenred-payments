
import requests

from .exceptions import APIError, Unauthorized, TransactionError


class APIProvider(object):
    CONTENT_TYPE = 'application/json; charset=utf-8'

    def __init__(self, client_id, client_secret, base_url, public_key):
        self.public_key = public_key
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url
        self.access_token = None

    @staticmethod
    def create_access_token(client_id, client_secret, public_key, base_url):
        login_url = APIProvider.get_endpoint_url(resource=None, action='Login', base_url=base_url)
        payload = {
            "Security": {
                "ClientIdentifier": client_id,
                "ClientSecret": client_secret
            }
        }
        response = APIProvider.do_request(
            url=login_url, payload=payload, headers={'Content-Type': APIProvider.CONTENT_TYPE}
        )
        return response['access_token']

    @staticmethod
    def get_endpoint_url(base_url, resource, action):
        if resource is not None:
            return "{}/{}/{}".format(base_url, resource, action)
        return "{}/{}".format(base_url, action)

    @staticmethod
    def do_request(url, headers, payload):
        try:
            response = requests.post(
                url,
                data=payload,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_error:
            raise APIError.create_from_http_error(http_error)

    def authorize(self, card_token, amount, description):
        payload = {
            "Authorize": {
                "CardToken": card_token,
                "Amount": amount,
                "Description": description,
                "AuthorizeIdentifier": None
            }
        }
        data = self.request_resource(resource='Payment', action='Authorize', payload=payload)
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
        data = self.request_resource(resource='Payment', action='Pay', payload=payload)
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
        data = self.request_resource(resource='Payment', action='Capture', payload=payload)
        return data['Capture']

    def refund(self, card_token, payment_identifier, amount, description):
        payload = {
            "Pay": {
                "CardToken": card_token,
                "Amount": amount,
                "Description": description,
                "PayIdentifier": payment_identifier
            }
        }
        resource = 'Payment/{}'.format(payment_identifier)
        data = self.request_resource(resource=resource, action='Refund', payload=payload)
        return data['Pay']

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
        data = self.request_resource(resource='PaymentMethod', action='Create', payload=payload)
        return data['PaymentMethod']

    def request_resource(self, resource, action, payload, renew_on_unauthorized=True):
        try:
            response = self.do_request(
                url=self.get_endpoint_url(resource=resource, action=action, base_url=self.base_url),
                headers=self._get_headers(),
                payload=payload
            )
        except Unauthorized:
            if renew_on_unauthorized:
                self.update_token()
                return self.request_resource(
                    resource=resource, action=action, payload=payload, renew_on_unauthorized=False
                )
            raise
        else:
            self.validate_response(response)
            return response

    @staticmethod
    def validate_response(response):
        if not response.get('Success', True):
            error_list = response.get('ErrorList') or []
            for error in error_list:
                raise TransactionError.create_from_code(error)
            raise TransactionError()

    def update_token(self):
        self.access_token = self.create_access_token(
            client_id=self.client_id,
            client_secret=self.client_secret,
            public_key=self.public_key,
            base_url=self.base_url
        )

    def _get_headers(self):
        if self.access_token is None:
            self.update_token()
        return {
            'Content-Type': APIProvider.CONTENT_TYPE,
            'access_token': self.access_token
        }

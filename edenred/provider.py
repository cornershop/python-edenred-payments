
import logging

import requests

from .exceptions import APIError, Unauthorized, TransactionErrors

logger = logging.getLogger(__name__)


class APIProvider(object):
    CONTENT_TYPE = 'application/json; charset=utf-8'

    def __init__(self, client_id, client_secret, base_url, public_key, access_token=None):
        self.public_key = public_key
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url
        self.access_token = access_token

    @classmethod
    def create_access_token(cls, client_id, client_secret, public_key, base_url):
        logger.debug("Retrieving Edenred access_token")
        login_url = cls.get_endpoint_url(resource=None, action='Login', base_url=base_url)
        payload = {
            "Security": {
                "ClientIdentifier": client_id,
                "ClientSecret": client_secret
            }
        }
        response = cls.do_request(
            url=login_url, payload=payload, headers={'Content-Type': cls.CONTENT_TYPE}
        )
        cls.validate_response(response)
        return response['access_token']

    @classmethod
    def get_endpoint_url(cls, base_url, resource, action):
        if resource is not None:
            return "{}/{}/{}".format(base_url, resource, action)
        return "{}/{}".format(base_url, action)

    @classmethod
    def do_request(cls, url, headers, payload):
        try:
            logger.debug("Requesting %s", url)
            response = requests.post(
                url,
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_error:
            raise APIError.create_from_http_error(http_error)

    @classmethod
    def validate_response(cls, response):
        if not response.get('Success', False):
            errors = response.get('ErrorList') or []
            raise TransactionErrors(response, errors)

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
            logger.debug('Response: %s', response)
            self.validate_response(response)
            return response

    def authorize(self, card_token, amount, description):
        payload = {
            "Authorize": {
                "CardToken": card_token,
                "Amount": amount,
                "Description": description,
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
                "AuthorizeIdentifier": authorize_identifier
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
                "CardToken": ""
            }
        }
        data = self.request_resource(resource='PaymentMethod', action='Create', payload=payload)
        return data['PaymentMethod']

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
            'Content-Type': self.CONTENT_TYPE,
            'authorization': self.access_token
        }

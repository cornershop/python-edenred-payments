
import os
from decimal import Decimal

from .providers import APIProvider
from .utils import PublicKey


class Edenred(object):
    def __init__(self, api_provider):
        self.api_provider = api_provider

    @staticmethod
    def create_client_from_env():
        client_id = os.environ['EDENREDPAYMENTS_ID']
        client_secret = os.environ['EDENREDPAYMENTS_SECRET']
        public_key_path = os.environ['EDENREDPAYMENTS_PUBLIC_KEY']
        base_url = os.environ['EDENREDPAYMENTS_URL']
        testing = bool(os.getenv('EDENREDPAYMENTS_TESTING'))
        return Edenred.create_client(client_id, client_secret, public_key_path, base_url, testing)

    @staticmethod
    def create_client(client_id, client_secret, public_key_path, base_url, testing=False):
        public_key = PublicKey(public_key_path, testing=testing)
        api_provider = APIProvider(
            client_id=client_id,
            client_secret=client_secret,
            public_key=public_key,
            base_url=base_url
        )
        return Edenred(api_provider)

    def register_card(self, card_number, cvv, expiration_month, expiration_year, username, user_id):
        response = self.api_provider.create_payment_method(
            card_number=card_number,
            cvv=cvv,
            expiration_month=expiration_month,
            expiration_year=expiration_year,
            username=username,
            user_id=user_id
        )
        return Card(response['CardToken'], self.api_provider)

    def retrieve_card(self, card_token):
        return Card(card_token, self.api_provider)

    def __eq__(self, other):
        return self.api_provider == other.api_provider

    def __repr__(self):
        return "Edenred({provider})".format(provider=repr(self.api_provider))

    __str__ = __repr__


class Card(object):
    def __init__(self, card_token, api_provider):
        self.api_provider = api_provider
        self.card_token = card_token

    def retrieve_authorization(self, charge_id):
        return Authorization(charge_id, self.card_token, self.api_provider)

    def authorize(self, amount, description):
        response = self.api_provider.authorize(
            card_token=self.card_token,
            amount=amount,
            description=description
        )
        return Authorization(response['AuthorizeIdentifier'], self, self.api_provider)

    def capture(self, amount, description):
        response = self.api_provider.pay(
            card_token=self.card_token,
            amount=amount,
            description=description
        )
        return Charge(response['PayIdentifier'], self, self.api_provider)

    def __eq__(self, other):
        return self.api_provider == other.api_provider and self.card_token == other.card_token


class Authorization(object):
    def __init__(self, charge_id, card, api_provider):
        self.api_provider = api_provider
        self.charge_id = charge_id
        self.card = card

    def capture(self, amount, description):
        response = self.api_provider.capture(
            card_token=self.card.card_token,
            authorize_identifier=self.charge_id,
            amount=amount,
            description=description
        )
        return Charge(response['CaptureIdentifier'], self.card, self.api_provider)

    def __eq__(self, other):
        return self.api_provider == other.api_provider \
            and self.charge_id == other.charge_id \
            and self.card == other.card


class Charge(object):
    def __init__(self, charge_id, card, api_provider):
        self.api_provider = api_provider
        self.charge_id = charge_id
        self.card = card

    def refund(self, amount, description):
        response = self.api_provider.refund(
            card_token=self.card.card_token,
            payment_identifier=self.charge_id,
            amount=amount,
            description=description
        )
        return Refund(self, Decimal(response['Amount']), self.api_provider)

    def __eq__(self, other):
        return self.api_provider == other.api_provider \
            and self.charge_id == other.charge_id \
            and self.card == other.card


class Refund(object):
    def __init__(self, charge, amount, api_provider):
        self.api_provider = api_provider
        self.charge = charge
        self.amount = amount

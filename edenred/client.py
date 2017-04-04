
from .provider import APIProvider


class Edenred(object):
    def __init__(self, api_provider):
        self.api_provider = api_provider

    @staticmethod
    def create_client(client_id, client_secret, public_key_path, provider_class=APIProvider):
        api_provider = provider_class.create_for_client(client_id, client_secret, public_key_path)
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
        return Authorization(response['AuthorizeIdentifier'], self.card_token, self.api_provider)

    def capture(self, amount, description):
        response = self.api_provider.pay(
            card_token=self.card_token,
            amount=amount,
            description=description
        )
        return Charge(response['PayIdentifier'], self.api_provider)

    def __eq__(self, other):
        return self.api_provider == other.api_provider and self.card_token == other.card_token


class Authorization(object):
    def __init__(self, charge_id, card_token, api_provider):
        self.api_provider = api_provider
        self.charge_id = charge_id
        self.card_token = card_token

    def capture(self, amount, description):
        response = self.api_provider.capture(
            card_token=self.card_token,
            authorize_identifier=self.charge_id,
            amount=amount,
            description=description
        )
        return Charge(response['CaptureIdentifier'], self.api_provider)

    def __eq__(self, other):
        return self.api_provider == other.api_provider and self.charge_id == other.charge_id


class Charge(object):
    def __init__(self, charge_id, api_provider):
        self.api_provider = api_provider
        self.charge_id = charge_id

    def __eq__(self, other):
        return self.api_provider == other.api_provider and self.charge_id == other.charge_id

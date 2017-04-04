
from unittest import TestCase

try:
    from unitttest import mock
except ImportError:
    import mock

from edenred.client import Edenred, Card, Authorization, Charge
from edenred.provider import APIProviderBase


class TestClient(TestCase):
    def setUp(self):
        self.provider = mock.Mock(spec=APIProviderBase)

    def test_init(self):
        client = Edenred(self.provider)

        self.assertEqual(self.provider, client.api_provider)

    @mock.patch('edenred.client.APIProvider.create_for_client')
    def test_factory_create(self, create_for_client):
        client_id = mock.Mock()
        client_secret = mock.Mock()
        public_key_path = mock.Mock()
        create_for_client.return_value = self.provider

        client = Edenred.create_client(client_id, client_secret, public_key_path)

        expected = Edenred(create_for_client.return_value)

        self.assertEqual(expected, client)
        create_for_client.assert_called_once_with(client_id, client_secret, public_key_path)

    def test_factory_create_custom(self):
        client_id = mock.Mock()
        client_secret = mock.Mock()
        public_key_path = mock.Mock()
        provider_class = mock.Mock()
        provider_class.create_for_client.return_value = self.provider

        client = Edenred.create_client(client_id, client_secret, public_key_path, provider_class)

        expected = Edenred(provider_class.create_for_client.return_value)

        self.assertEqual(expected, client)
        provider_class.create_for_client.assert_called_once_with(client_id, client_secret, public_key_path)

    def test_register_card(self):
        card_number = mock.Mock()
        cvv = mock.Mock()
        expiration_month = mock.Mock()
        expiration_year = mock.Mock()
        username = mock.Mock()
        user_id = mock.Mock()
        card_token = mock.Mock()
        client = Edenred(self.provider)
        self.provider.create_payment_method.return_value = {'CardToken': card_token}
        expected = Card(card_token, self.provider)

        card = client.register_card(card_number, cvv, expiration_month, expiration_year, username, user_id)

        self.assertEqual(expected, card)
        self.provider.create_payment_method.assert_called_once_with(
            card_number=card_number,
            cvv=cvv,
            expiration_month=expiration_month,
            expiration_year=expiration_year,
            username=username,
            user_id=user_id
        )

    def test_retrieve_card(self):
        card_token = mock.Mock()
        expected = Card(card_token, self.provider)
        client = Edenred(self.provider)

        self.assertEqual(expected, client.retrieve_card(card_token))


class TestCard(TestCase):
    def setUp(self):
        self.provider = mock.Mock(spec=APIProviderBase)
        self.card_token = mock.Mock()

    def test_init(self):
        card = Card(self.card_token, self.provider)

        self.assertEqual(self.provider, card.api_provider)
        self.assertEqual(self.card_token, card.card_token)

    def test_retrieve_authorization(self):
        charge_id = mock.Mock()
        expected = Authorization(charge_id, self.card_token, self.provider)
        card = Card(self.card_token, self.provider)

        self.assertEqual(expected, card.retrieve_authorization(charge_id))

    def test_authorize(self):
        card = Card(self.card_token, self.provider)
        charge_id = mock.Mock()
        amount = mock.Mock()
        description = mock.Mock()
        expected = Authorization(charge_id, self.card_token, self.provider)
        self.provider.authorize.return_value = {'AuthorizeIdentifier': charge_id}

        self.assertEqual(expected, card.authorize(amount, description))
        self.provider.authorize.assert_called_once_with(
            card_token=self.card_token,
            amount=amount,
            description=description
        )

    def test_capture(self):
        card = Card(self.card_token, self.provider)
        charge_id = mock.Mock()
        amount = mock.Mock()
        description = mock.Mock()
        expected = Charge(charge_id, self.provider)
        self.provider.pay.return_value = {'PayIdentifier': charge_id}

        self.assertEqual(expected, card.capture(amount, description))
        self.provider.pay.assert_called_once_with(
            card_token=self.card_token,
            amount=amount,
            description=description
        )


class TestAuthorization(TestCase):
    def setUp(self):
        self.provider = mock.Mock(spec=APIProviderBase)
        self.charge_id = mock.Mock()
        self.card_token = mock.Mock()

    def test_init(self):
        authorization = Authorization(self.charge_id, self.card_token, self.provider)

        self.assertEqual(self.provider, authorization.api_provider)
        self.assertEqual(self.charge_id, authorization.charge_id)

    def test_capture(self):
        authorization = Authorization(self.charge_id, self.card_token, self.provider)
        amount = mock.Mock()
        description = mock.Mock()
        expected = Charge(self.charge_id, self.provider)
        self.provider.capture.return_value = {'CaptureIdentifier': self.charge_id}

        self.assertEqual(expected, authorization.capture(amount, description))
        self.provider.capture.assert_called_once_with(
            authorize_identifier=self.charge_id,
            card_token=self.card_token,
            amount=amount,
            description=description
        )


class TestCharge(TestCase):
    def test_init(self):
        provider = mock.Mock(spec=APIProviderBase)
        charge_id = mock.Mock()
        charge = Charge(charge_id, provider)

        self.assertEqual(provider, charge.api_provider)
        self.assertEqual(charge_id, charge.charge_id)


from decimal import Decimal
from unittest import TestCase
try:
    from unitttest import mock
except ImportError:
    import mock

from edenred.client import Edenred, Card, Authorization, Charge, Refund
from edenred.providers import APIProvider


class TestClient(TestCase):
    def setUp(self):
        self.provider = mock.Mock(spec=APIProvider)

    def test_init(self):
        client = Edenred(self.provider)

        self.assertEqual(self.provider, client.api_provider)

    @mock.patch('edenred.client.Edenred.create_client')
    def test_factore_create_from_env(self, create_client):
        client_id = 'client_id'
        client_secret = 'client_secret'
        public_key_path = 'public_key_path'
        base_url = 'base_url'
        environ = {
            'EDENREDPAYMENTS_ID': client_id,
            'EDENREDPAYMENTS_SECRET': client_secret,
            'EDENREDPAYMENTS_PUBLIC_KEY': public_key_path,
            'EDENREDPAYMENTS_URL': base_url
        }

        with mock.patch.dict('edenred.client.os.environ', environ):
            result = Edenred.create_client_from_env()

        create_client.assert_called_once_with(
            client_id, client_secret, public_key_path, base_url, False
        )
        self.assertEqual(create_client.return_value, result)

    @mock.patch('edenred.client.Edenred.create_client')
    def test_factore_create_from_env_testing(self, create_client):
        client_id = 'client_id'
        client_secret = 'client_secret'
        public_key_path = 'public_key_path'
        base_url = 'base_url'
        environ = {
            'EDENREDPAYMENTS_ID': client_id,
            'EDENREDPAYMENTS_SECRET': client_secret,
            'EDENREDPAYMENTS_PUBLIC_KEY': public_key_path,
            'EDENREDPAYMENTS_URL': base_url,
            'EDENREDPAYMENTS_TESTING': '1',
        }

        with mock.patch.dict('edenred.client.os.environ', environ):
            result = Edenred.create_client_from_env()

        create_client.assert_called_once_with(
            client_id, client_secret, public_key_path, base_url, True
        )
        self.assertEqual(create_client.return_value, result)

    @mock.patch('edenred.client.PublicKey')
    @mock.patch('edenred.client.APIProvider')
    def test_factory_create(self, APIProvider, PublicKey):
        client_id = mock.Mock(spec=str)
        client_secret = mock.Mock(spec=str)
        public_key_path = mock.Mock(spec=str)
        public_key = PublicKey.return_value
        base_url = mock.Mock(spec=str)
        APIProvider.return_value = self.provider

        client = Edenred.create_client(client_id, client_secret, public_key_path, base_url)

        expected = Edenred(APIProvider.return_value)

        PublicKey.assert_called_once_with(public_key_path, testing=False)
        APIProvider.assert_called_once_with(
            client_id=client_id, client_secret=client_secret, public_key=public_key, base_url=base_url
        )
        self.assertEqual(expected, client)

    @mock.patch('edenred.client.PublicKey')
    @mock.patch('edenred.client.APIProvider')
    def test_factory_create_testing(self, APIProvider, PublicKey):
        client_id = mock.Mock(spec=str)
        client_secret = mock.Mock(spec=str)
        public_key_path = mock.Mock(spec=str)
        public_key = PublicKey.return_value
        base_url = mock.Mock(spec=str)
        testing = mock.Mock(spec=bool)
        APIProvider.return_value = self.provider

        client = Edenred.create_client(client_id, client_secret, public_key_path, base_url, testing=testing)

        expected = Edenred(APIProvider.return_value)

        PublicKey.assert_called_once_with(public_key_path, testing=testing)
        APIProvider.assert_called_once_with(
            client_id=client_id, client_secret=client_secret, public_key=public_key, base_url=base_url
        )
        self.assertEqual(expected, client)

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
        self.provider = mock.Mock(spec=APIProvider)
        self.card_token = mock.Mock()
        self.amount = Decimal('123.45')
        self.amount_in_cents = int(self.amount * 100)

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
        amount = Decimal('123.45')
        description = mock.Mock()
        expected = Authorization(charge_id, card, self.provider)
        self.provider.authorize.return_value = {'AuthorizeIdentifier': charge_id}

        self.assertEqual(expected, card.authorize(self.amount, description))
        self.provider.authorize.assert_called_once_with(
            card_token=self.card_token,
            amount=self.amount_in_cents,
            description=description
        )

    def test_capture(self):
        card = Card(self.card_token, self.provider)
        charge_id = mock.Mock()
        amount = Decimal('123.45')
        description = mock.Mock()
        expected = Charge(charge_id, card, self.provider)
        self.provider.pay.return_value = {'AuthorizeIdentifier': charge_id}

        self.assertEqual(expected, card.capture(self.amount, description))
        self.provider.pay.assert_called_once_with(
            card_token=self.card_token,
            amount=self.amount_in_cents,
            description=description
        )


class TestAuthorization(TestCase):
    def setUp(self):
        self.provider = mock.Mock(spec=APIProvider)
        self.charge_id = mock.Mock()
        self.card = Card(mock.Mock(spec=str), self.provider)
        self.amount = Decimal('123.45')
        self.amount_in_cents = int(self.amount * 100)

    def test_init(self):
        authorization = Authorization(self.charge_id, self.card, self.provider)

        self.assertEqual(self.provider, authorization.api_provider)
        self.assertEqual(self.card, authorization.card)
        self.assertEqual(self.charge_id, authorization.charge_id)

    def test_capture(self):
        authorization = Authorization(self.charge_id, self.card, self.provider)
        amount = mock.Mock()
        description = mock.Mock()
        expected = Charge(self.charge_id, self.card, self.provider)
        self.provider.capture.return_value = {'AuthorizeIdentifier': self.charge_id}

        self.assertEqual(expected, authorization.capture(self.amount, description))
        self.provider.capture.assert_called_once_with(
            authorize_identifier=self.charge_id,
            card_token=self.card.card_token,
            amount=self.amount_in_cents,
            description=description
        )


class TestRefund(TestCase):
    def setUp(self):
        self.provider = mock.Mock(spec=APIProvider)
        self.charge_id = mock.Mock(spec=str)
        self.card = Card(mock.Mock(spec=str), self.provider)
        self.amount = Decimal('123.45')
        self.amount_in_cents = int(self.amount * 100)

    def test_init(self):
        amount = mock.Mock(spec=Decimal)
        charge = Charge(self.charge_id, self.card, self.provider)

        refund = Refund(charge, amount, self.provider)

        self.assertEqual(charge, refund.charge)
        self.assertEqual(amount, refund.amount)

    @mock.patch('edenred.client.amount_with_decimals')
    def test_refund(self, amount_with_decimals):
        charge = Charge(self.charge_id, self.card, self.provider)
        amount = mock.Mock(spec=Decimal)
        description = mock.Mock(spec=str)
        amount_response = 101010109
        self.provider.refund.return_value = {'Amount': amount_response}

        refund = charge.refund(self.amount, description)

        self.assertEqual(charge, refund.charge)
        self.assertEqual(amount_with_decimals.return_value, refund.amount)


class TestCharge(TestCase):
    def setUp(self):
        self.provider = mock.Mock(spec=APIProvider)
        self.charge_id = mock.Mock(spec=str)
        self.card = mock.Mock(spec=Card)

    def test_init(self):
        charge = Charge(self.charge_id, self.card, self.provider)

        self.assertEqual(self.provider, charge.api_provider)
        self.assertEqual(self.charge_id, charge.charge_id)

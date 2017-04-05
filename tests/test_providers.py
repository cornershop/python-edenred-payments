
from unittest import TestCase
try:
    from unitttest import mock
except ImportError:
    import mock

from edenred.providers import APIProvider
from edenred.utils import PublicKey


class TestAPIProvider(TestCase):

    def test_init(self):
        public_key = mock.Mock(spec=PublicKey)
        access_token = mock.Mock(spec=str)
        provider = APIProvider(access_token=access_token, public_key=public_key)

        self.assertFalse(provider.testing)
        self.assertEqual(access_token, provider.access_token)
        self.assertEqual(public_key, provider.public_key)

    def test_init_testing(self):
        public_key = mock.Mock(spec=PublicKey)
        access_token = mock.Mock(spec=str)
        provider = APIProvider(access_token=access_token, public_key=public_key, testing=True)

        self.assertTrue(provider.testing)
        self.assertEqual(access_token, provider.access_token)
        self.assertEqual(public_key, provider.public_key)

    @mock.patch('edenred.providers.requests')
    def test_do_request(self, requests):
        payload = mock.Mock(spec=dict)
        headers = mock.Mock(spec=dict)
        url = mock.Mock(spec=str)

        result = APIProvider.do_request(url=url, headers=headers, payload=payload)

        self.assertEqual(requests.post.return_value.json.return_value, result)
        requests.post.assert_called_once_with(url, data=payload, headers=headers)

    @mock.patch('edenred.providers.APIProvider.do_request')
    @mock.patch('edenred.providers.APIProvider.get_endpoint_url')
    @mock.patch('edenred.providers.APIProvider._get_headers')
    def test_request_resource(self, _get_headers, get_endpoint_url, do_request):
        public_key = mock.Mock(spec=PublicKey)
        access_token = mock.Mock(spec=str)
        testing = mock.Mock(spec=bool)
        payload = mock.Mock(spec=dict)
        resource = mock.Mock(spec=str)

        provider = APIProvider(access_token=access_token, public_key=public_key, testing=testing)
        result = provider.request_resource(resource=resource, payload=payload)

        self.assertEqual(do_request.return_value, result)
        do_request.assert_called_once_with(
            url=get_endpoint_url.return_value, payload=payload, headers=_get_headers.return_value
        )
        get_endpoint_url.assert_called_once_with(resource=resource, testing=testing)

    def test__get_headers(self):
        public_key = mock.Mock(spec=PublicKey)
        access_token = mock.Mock(spec=str)

        provider = APIProvider(access_token=access_token, public_key=public_key)

        self.assertEqual({'access_token': access_token}, provider._get_headers())

    @mock.patch('edenred.providers.APIProvider.get_public_key')
    @mock.patch('edenred.providers.APIProvider.create_access_token')
    @mock.patch('edenred.providers.APIProvider.get_base_url')
    def test_create_for_client(self, get_base_url, create_access_token, get_public_key):
        client_id = mock.Mock(spec=str)
        client_secret = mock.Mock(spec=str)
        public_key_path = mock.Mock(spec=str)

        expected = APIProvider(
            access_token=create_access_token.return_value,
            public_key=get_public_key.return_value,
        )

        provider = APIProvider.create_for_client(client_id, client_secret, public_key_path)

        self.assertEqual(expected, provider)
        get_public_key.assert_called_once_with(public_key_path)
        create_access_token.assert_called_once_with(client_id, client_secret, get_public_key.return_value, False)

    @mock.patch('edenred.providers.APIProvider.get_public_key')
    @mock.patch('edenred.providers.APIProvider.create_access_token')
    @mock.patch('edenred.providers.APIProvider.get_base_url')
    def test_create_for_client_testing(self, get_base_url, create_access_token, get_public_key):
        client_id = mock.Mock(spec=str)
        client_secret = mock.Mock(spec=str)
        public_key_path = mock.Mock(spec=str)

        expected = APIProvider(
            access_token=create_access_token.return_value,
            public_key=get_public_key.return_value,
            testing=True
        )

        provider = APIProvider.create_for_client(client_id, client_secret, public_key_path, testing=True)

        self.assertEqual(expected, provider)
        get_public_key.assert_called_once_with(public_key_path)
        create_access_token.assert_called_once_with(client_id, client_secret, get_public_key.return_value, True)

    def test_get_public_key(self):
        public_key_path = mock.Mock(spec=str)

        public_key = PublicKey(public_key_path)

        self.assertEqual(public_key, APIProvider.get_public_key(public_key_path))

    @mock.patch('edenred.providers.APIProvider.get_base_url')
    def test_get_endpoint_url(self, get_base_url):
        get_base_url.return_value = mock.Mock(spec=str)
        resource = mock.Mock(spec=str)
        testing = mock.Mock()

        self.assertEqual(
            "{}/{}".format(get_base_url.return_value, resource),
            APIProvider.get_endpoint_url(resource, testing)
        )
        get_base_url.assert_called_once_with(testing)

    @mock.patch('edenred.providers.APIProvider.get_endpoint_url')
    @mock.patch('edenred.providers.APIProvider.do_request')
    def test_create_access_token_success(self, do_request, get_endpoint_url):
        client_id = mock.Mock(spec=str)
        client_secret = mock.Mock(spec=str)
        public_key = mock.Mock(spec=PublicKey)
        access_token = mock.Mock(spec=str)
        testing = mock.Mock(spec=bool)
        payload = {
            "Security": {
                "ClientIdentifier": client_id,
                "ClientSecret": client_secret
            }
        }
        do_request.return_value = {
            "Success": True,
            "access_token": access_token,
            "ErrorList": None
        }

        self.assertEqual(
            access_token,
            APIProvider.create_access_token(client_id, client_secret, public_key, testing=testing)
        )
        do_request.assert_called_once_with(
            url=get_endpoint_url.return_value,
            payload=payload,
            headers={}
        )
        get_endpoint_url.assert_called_once_with('Login', testing=testing)


class TestCreatePaymentMethod(TestCase):
    def setUp(self):
        self.public_key = mock.Mock(spec=PublicKey)
        self.access_token = mock.Mock(spec=str)
        self.provider = APIProvider(self.public_key, self.access_token)

    @mock.patch('edenred.providers.APIProvider.request_resource')
    def test_create_payment_method(self, request_resource):
        card_number = mock.Mock(spec=str)
        cvv = mock.Mock(spec=str)
        expiration_month = mock.Mock(spec=str)
        expiration_year = mock.Mock(spec=str)
        encrypted = {
            card_number: mock.Mock(spec=str),
            cvv: mock.Mock(spec=str),
            expiration_month: mock.Mock(spec=str),
            expiration_year: mock.Mock(spec=str)
        }
        self.public_key.encrypt.side_effect = lambda x: encrypted[x]

        username = mock.Mock(spec=str)
        user_id = mock.Mock(spec=str)
        expected_payload = {
            "PaymentMethod": {
                "CardNumber": encrypted[card_number],
                "CardCVV": encrypted[cvv],
                "CardExpirationMonth": encrypted[expiration_month],
                "CardExpirationYear": encrypted[expiration_year],
                "UserLogin": username,
                "UserIdentifier": user_id,
                "CardToken": None
            }
        }

        card_token = mock.Mock(spec=str)
        request_resource.return_value = {
            "PaymentMethod": {
                "CardToken": card_token
            },
            "Success": True,
            "ErrorList": []
        }

        result = self.provider.create_payment_method(
            card_number=card_number,
            cvv=cvv,
            expiration_month=expiration_month,
            expiration_year=expiration_year,
            username=username,
            user_id=user_id
        )
        self.assertEqual(request_resource.return_value['PaymentMethod'], result)
        request_resource.assert_called_once_with('CreatePaymentMethod', expected_payload)


class TestCapture(TestCase):
    def setUp(self):
        self.public_key = mock.Mock(spec=PublicKey)
        self.access_token = mock.Mock(spec=str)
        self.provider = APIProvider(self.public_key, self.access_token)

    @mock.patch('edenred.providers.APIProvider.request_resource')
    def test_capture(self, request_resource):
        card_token = mock.Mock(spec=str)
        authorize_identifier = mock.Mock(spec=str)
        description = mock.Mock(spec=str)
        amount = mock.Mock(spec=str)

        expected_payload = {
            "Capture": {
                "CardToken": card_token,
                "Amount": amount,
                "Description": description,
                "AuthorizeIdentifier": authorize_identifier,
                "CaptureIdentifier": None
            }
        }
        charge_id = mock.Mock(spec=str)
        request_resource.return_value = {
            "Capture": {
                "CaptureIdentifier": charge_id
            },
            "Success": True,
            "ErrorList": []
        }

        result = self.provider.capture(
            card_token=card_token,
            authorize_identifier=authorize_identifier,
            description=description,
            amount=amount
        )
        self.assertEqual(request_resource.return_value['Capture'], result)
        request_resource.assert_called_once_with('Capture', expected_payload)


class TestAuthorize(TestCase):
    def setUp(self):
        self.public_key = mock.Mock(spec=PublicKey)
        self.access_token = mock.Mock(spec=str)
        self.provider = APIProvider(self.public_key, self.access_token)

    @mock.patch('edenred.providers.APIProvider.request_resource')
    def test_authorize(self, request_resource):
        card_token = mock.Mock(spec=str)
        description = mock.Mock(spec=str)
        amount = mock.Mock(spec=str)

        expected_payload = {
            "Authorize": {
                "CardToken": card_token,
                "Amount": amount,
                "Description": description,
                "AuthorizeIdentifier": None
            }
        }
        charge_id = mock.Mock(spec=str)
        request_resource.return_value = {
            "Authorize": {
                "AuthorizeIdentifier": charge_id
            },
            "Success": True,
            "ErrorList": []
        }

        result = self.provider.authorize(
            card_token=card_token,
            amount=amount,
            description=description
        )
        self.assertEqual(request_resource.return_value['Authorize'], result)
        request_resource.assert_called_once_with('Authorize', expected_payload)


class TestPay(TestCase):
    def setUp(self):
        self.public_key = mock.Mock(spec=PublicKey)
        self.access_token = mock.Mock(spec=str)
        self.provider = APIProvider(self.public_key, self.access_token)

    @mock.patch('edenred.providers.APIProvider.request_resource')
    def test_pay(self, request_resource):
        card_token = mock.Mock(spec=str)
        description = mock.Mock(spec=str)
        amount = mock.Mock(spec=str)

        expected_payload = {
            "Pay": {
                "CardToken": card_token,
                "Amount": amount,
                "Description": description,
                "PayIdentifier": None
            }
        }
        charge_id = mock.Mock(spec=str)
        request_resource.return_value = {
            "Pay": {
                "PayIdentifier": charge_id
            },
            "Success": True,
            "ErrorList": []
        }

        result = self.provider.pay(
            card_token=card_token,
            amount=amount,
            description=description
        )
        self.assertEqual(request_resource.return_value['Pay'], result)
        request_resource.assert_called_once_with('Pay', expected_payload)


from unittest import TestCase
try:
    from unitttest import mock
except ImportError:
    import mock

from requests.exceptions import HTTPError

from edenred.providers import APIProvider
from edenred.utils import PublicKey
from edenred.exceptions import APIError, Unauthorized


class TestAPIProvider(TestCase):

    def test_init(self):
        public_key = mock.Mock(spec=PublicKey)
        base_url = mock.Mock(spec=str)
        client_id = mock.Mock(spec=str)
        client_secret = mock.Mock(spec=str)
        provider = APIProvider(
            client_id=client_id, client_secret=client_secret, base_url=base_url, public_key=public_key
        )

        self.assertEqual(client_id, provider.client_id)
        self.assertEqual(client_secret, provider.client_secret)
        self.assertEqual(public_key, provider.public_key)
        self.assertIsNone(provider.access_token)

    def test_get_headers_logged(self):
        public_key = mock.Mock(spec=PublicKey)
        base_url = mock.Mock(spec=str)
        client_id = mock.Mock(spec=str)
        client_secret = mock.Mock(spec=str)
        provider = APIProvider(
            client_id=client_id, client_secret=client_secret, base_url=base_url, public_key=public_key
        )
        provider.access_token = mock.Mock(spec=str)
        expected = {
            'access_token': provider.access_token,
            'Content-Type': 'application/json; charset=utf-8'
        }

        self.assertEqual(expected, provider._get_headers())

    @mock.patch('edenred.providers.APIProvider.create_access_token')
    def test_get_headers_notlogged(self, create_access_token):
        public_key = mock.Mock(spec=PublicKey)
        base_url = mock.Mock(spec=str)
        client_id = mock.Mock(spec=str)
        client_secret = mock.Mock(spec=str)
        provider = APIProvider(
            client_id=client_id, client_secret=client_secret, base_url=base_url, public_key=public_key
        )
        expected = {
            'access_token': create_access_token.return_value,
            'Content-Type': 'application/json; charset=utf-8'
        }

        self.assertEqual(expected, provider._get_headers())
        self.assertEqual(create_access_token.return_value, provider.access_token)
        create_access_token.assert_called_once_with(
            client_id=client_id, client_secret=client_secret, public_key=public_key, base_url=base_url
        )

    def test_get_endpoint_url(self):
        base_url = mock.Mock(spec=str)
        resource = mock.Mock(spec=str)

        self.assertEqual(
            "{}/{}".format(base_url, resource),
            APIProvider.get_endpoint_url(resource=resource, base_url=base_url)
        )

    @mock.patch('edenred.providers.APIProvider.get_endpoint_url')
    @mock.patch('edenred.providers.APIProvider.do_request')
    def test_create_access_token_success(self, do_request, get_endpoint_url):
        client_id = mock.Mock(spec=str)
        client_secret = mock.Mock(spec=str)
        public_key = mock.Mock(spec=PublicKey)
        access_token = mock.Mock(spec=str)
        base_url = mock.Mock(spec=str)
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
            APIProvider.create_access_token(client_id, client_secret, public_key, base_url)
        )
        do_request.assert_called_once_with(
            url=get_endpoint_url.return_value,
            payload=payload,
            headers={'Content-Type': 'application/json; charset=utf-8'}
        )
        get_endpoint_url.assert_called_once_with(resource='Login', base_url=base_url)


class TestDoRequest(TestCase):

    @mock.patch('edenred.providers.requests')
    def test_do_request(self, requests):
        payload = mock.Mock(spec=dict)
        headers = mock.Mock(spec=dict)
        url = mock.Mock(spec=str)
        response = requests.post.return_value

        result = APIProvider.do_request(url=url, headers=headers, payload=payload)

        self.assertEqual(requests.post.return_value.json.return_value, result)
        requests.post.assert_called_once_with(url, data=payload, headers=headers)
        response.raise_for_status.assert_called_once_with()

    @mock.patch('edenred.providers.requests.post')
    def test_do_request_http_error(self, requests_post):
        payload = mock.Mock(spec=dict)
        headers = mock.Mock(spec=dict)
        url = mock.Mock(spec=str)
        response = requests_post.return_value
        response.raise_for_status.side_effect = HTTPError(response=mock.Mock())

        with self.assertRaises(APIError, http_error=response.raise_for_status.side_effect):
            APIProvider.do_request(url=url, headers=headers, payload=payload)


class ProviderBaseMixin(object):
    def create_provider(self, access_token=None):
        public_key = mock.Mock(spec=PublicKey)
        base_url = mock.Mock(spec=str)
        client_id = mock.Mock(spec=str)
        client_secret = mock.Mock(spec=str)
        return APIProvider(
            client_id=client_id, client_secret=client_secret, base_url=base_url, public_key=public_key
        )

    def setUp(self):
        self.access_token = mock.Mock(spec=str)
        self.provider = self.create_provider(self.access_token)


class TestRequestResource(ProviderBaseMixin, TestCase):

    @mock.patch('edenred.providers.APIProvider.do_request')
    @mock.patch('edenred.providers.APIProvider.get_endpoint_url')
    @mock.patch('edenred.providers.APIProvider._get_headers')
    def test_request_resource(self, _get_headers, get_endpoint_url, do_request):
        resource = mock.Mock(spec=str)
        payload = mock.Mock(spec=dict)

        result = self.provider.request_resource(resource=resource, payload=payload)

        self.assertEqual(do_request.return_value, result)
        do_request.assert_called_once_with(
            url=get_endpoint_url.return_value, payload=payload, headers=_get_headers.return_value
        )
        get_endpoint_url.assert_called_once_with(resource=resource, base_url=self.provider.base_url)

    @mock.patch('edenred.providers.APIProvider.update_token')
    @mock.patch('edenred.providers.APIProvider.do_request')
    @mock.patch('edenred.providers.APIProvider.get_endpoint_url')
    @mock.patch('edenred.providers.APIProvider._get_headers')
    def test_request_resource_unauthorized(self, _get_headers, get_endpoint_url, do_request, update_token):
        resource = mock.Mock(spec=str)
        payload = mock.Mock(spec=dict)
        expected = mock.Mock()
        do_request.side_effect = [Unauthorized(HTTPError()), expected]

        result = self.provider.request_resource(resource=resource, payload=payload)

        self.assertEqual(expected, result)

    @mock.patch('edenred.providers.APIProvider.update_token')
    @mock.patch('edenred.providers.APIProvider.do_request')
    @mock.patch('edenred.providers.APIProvider.get_endpoint_url')
    @mock.patch('edenred.providers.APIProvider._get_headers')
    def test_request_resource_unauthorized_twice(self, _get_headers, get_endpoint_url, do_request, update_token):
        resource = mock.Mock(spec=str)
        payload = mock.Mock(spec=dict)
        expected = HTTPError()
        do_request.side_effect = [Unauthorized(HTTPError()), Unauthorized(expected)]

        with self.assertRaises(Unauthorized, http_error=expected):
            self.provider.request_resource(resource=resource, payload=payload)


class TestCreatePaymentMethod(ProviderBaseMixin, TestCase):

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
        self.provider.public_key.encrypt.side_effect = lambda x: encrypted[x]

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


class TestCapture(ProviderBaseMixin, TestCase):

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


class TestAuthorize(ProviderBaseMixin, TestCase):

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


class TestPay(ProviderBaseMixin, TestCase):

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

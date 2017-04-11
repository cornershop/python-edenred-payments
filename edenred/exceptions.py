# encoding=UTF-8
from __future__ import unicode_literals


class APIError(Exception):
    ERROR_CODE = None
    ERROR_MESSAGE = 'API Error'

    def __init__(self, http_error):
        super(APIError, self).__init__(self.ERROR_MESSAGE)
        self.http_error = http_error

    def get_error_message(self):
        meta = self.http_error.response.json()['meta']
        for message in meta['messages']:
            if message['code'] == self.ERROR_CODE:
                return message['message']
        return meta['status']

    @staticmethod
    def create_from_http_error(error):
        if error.response.status_code == Unauthorized.status_code:
            return Unauthorized(error)
        return APIError(error)


class Unauthorized(APIError):
    status_code = 401


class TransactionError(Exception):
    code = 99
    description = "Error desconocido"

    def __init__(self, code=None):
        if code is not None:
            self.code = code
        super(TransactionError, self).__init__(self.description)

    @staticmethod
    def create_from_code(code):
        if code == AccessDenied.code:
            return AccessDenied()
        elif code == InvalidCard.code:
            return InvalidCard()
        elif code == AuthorizationOngoing.code:
            return AuthorizationOngoing()
        elif code == CaptureOngoing.code:
            return CaptureOngoing()
        elif code == CannotProcess.code:
            return CannotProcess()


class AccessDenied(TransactionError):
    code = 100
    description = "Sin acceso al recurso"


class InvalidCard(TransactionError):
    code = 101
    description = "Tarjeta no valida, bloqueada, sin saldo, datos de verifación incorrectos"


class AuthorizationOngoing(TransactionError):
    code = 102
    description = "Autorización en curso"


class CaptureOngoing(TransactionError):
    code = 103
    description = "Captura en curso"


class CannotProcess(TransactionError):
    code = 104
    description = "No se pudo procesar la operación"

from django.conf import settings


from abc import ABC, abstractmethod
from base64 import b64decode, b64encode
from decimal import Decimal
from traceback import format_exc

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from django.conf import settings

from utils.helper_functions import log_error


class AESCipher:

    def __init__(self, key, vector):
        self.key = bytes(key, 'ascii')
        self.vector = bytes(vector, 'ascii')

    def encrypt(self, raw):
        if not raw:
            return raw

        raw = bytes(raw, "utf8")
        cipher = AES.new(self.key, AES.MODE_CBC, self.vector)
        return b64encode(cipher.encrypt(pad(raw, AES.block_size))).decode("utf8")

    def decrypt(self, enc):
        if any((not enc, enc == "null", enc == "None", enc is None)):
            return enc

        text = b64decode(enc)
        cipher = AES.new(self.key, AES.MODE_CBC, self.vector)
        return unpad(cipher.decrypt(text), AES.block_size).decode("utf8")

    def encrypt_nested(self, obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if any((isinstance(value, str), isinstance(value, float), isinstance(value, Decimal),
                        isinstance(value, int))):
                    obj[key] = self.encrypt(str(value))
                else:
                    obj[key] = self.encrypt_nested(value)

        elif isinstance(obj, list):
            for index, value in enumerate(obj):
                obj[index] = self.encrypt_nested(value)

        else:
            obj = self.encrypt(str(obj))

        return obj

    def decrypt_nested(self, obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, str):
                    obj[key] = self.decrypt(value)
                else:
                    obj[key] = self.decrypt_nested(value)

        elif isinstance(obj, list):
            for index, value in enumerate(obj):
                obj[index] = self.decrypt_nested(value)

        else:
            obj = self.decrypt(str(obj))
        return obj

    def decrypt_body(self, obj):
        try:
            return self.decrypt_nested(obj)
        except Exception as e:
            log_error(title=str(e), error=format_exc(), request=f"Decrypt --- {obj}")
            return None

    def encrypt_body(self, obj):
        try:
            return self.encrypt_nested(obj)
        except Exception as e:
            log_error(title=str(e), error=format_exc(), request=f"Encrypt --- {obj}")
            return None


def decrypt_request_body(data: dict) -> tuple:
    if settings.USE_ENCRYPTION:
        aes = AESCipher(settings.ENCRYPTION_KEY, settings.INITIALIZATION_VECTOR)
        data = aes.decrypt_body(data)
        if data:
            return True, data
        return False, "Request Body could not be understood !"
    return True, data


def encrypt_response(data: dict | list | str) -> dict | list | str:
    if settings.USE_ENCRYPTION:
        aes = AESCipher(settings.ENCRYPTION_KEY, settings.INITIALIZATION_VECTOR)
        return aes.encrypt_body(data)
    return data


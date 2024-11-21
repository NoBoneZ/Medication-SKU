from rest_framework.exceptions import ValidationError
from rest_framework.fields import EmailField, CharField
from rest_framework.serializers import Serializer

from account.models import User
from utils.helper_functions import compound_password_validator


class SignUpSerializer(Serializer):
    email = EmailField()
    password = CharField()


    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already in use")

        status, message = compound_password_validator(password=password)
        if not status:
            raise ValidationError(message, "password")

        return attrs


class SignInSerializer(Serializer):
    email = CharField()
    password = CharField()


class VerifyOTPSerializer(Serializer):
    otp = CharField(min_length=5)

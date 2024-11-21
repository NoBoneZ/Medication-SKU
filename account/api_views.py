from django.contrib.auth.hashers import make_password
from django.utils.timezone import now
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED
from rest_framework_simplejwt.tokens import RefreshToken

from account.models import User, UserAccountActivationOTP
from account.serializers import SignInSerializer, SignUpSerializer, VerifyOTPSerializer
from utils.authorization_utils import RequestAuthentication, UserPermission
from utils.encryption_utils import decrypt_request_body
from utils.exception_handler import api_safe_execution
from utils.mixins import AllowAnyMixin
from utils.tasks import send_otp_for_verification


class SignUpAPIView(AllowAnyMixin):

    @api_safe_execution
    def post(self, request, *args, **kwargs):
        status, data = decrypt_request_body(data=request.data)
        if not status:
            return Response(data=data, status=HTTP_400_BAD_REQUEST)

        serializer = SignUpSerializer(data=data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email").lower()
            password = make_password(serializer.validated_data.get("password"))
            user_obj = User.objects.create(password=password, email=email, username=email)
            send_otp_for_verification(user_id=user_obj.id, email=email)
            refresh_token = RefreshToken.for_user(user_obj)

            return Response(data=(dict(access_token=str(refresh_token.access_token), refresh_token=str(refresh_token))),
                            status=HTTP_201_CREATED)
        return Response(data=dict(errors=serializer.errors), status=HTTP_400_BAD_REQUEST)



class SignInAPIView(AllowAnyMixin):

    @api_safe_execution
    def post(self, request, *args, **kwargs):
        status, data = decrypt_request_body(data=request.data)
        if not status:
            return Response(data=data, status=HTTP_400_BAD_REQUEST)

        serializer = SignInSerializer(data=data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email").lower()
            password = serializer.validated_data.get("password")

            user = User.objects.filter(email=email).first()

            if not user:
                return Response(data=dict(errors="Invalid Credentials"), status=HTTP_400_BAD_REQUEST)

            if not user.check_password(password):
                return Response(data=dict(errors="Invalid Credentials"), status=HTTP_400_BAD_REQUEST)

            if not user.is_account_verified:
                send_otp_for_verification(user_id=user.id, email=user.email)

            refresh_token = RefreshToken.for_user(user)
            data = dict(
                token=dict(access_token=str(refresh_token.access_token), refresh_token=str(refresh_token)),
                is_account_verified=user.is_account_verified
            )
            return Response(data=data, status=HTTP_201_CREATED)
        return Response(data=dict(errors=serializer.errors), status=HTTP_400_BAD_REQUEST)



class VerifyOTPAPIView(RequestAuthentication, CreateAPIView):
    permission_classes = (UserPermission,)

    @api_safe_execution
    def post(self, request, *args, **kwargs):
        status, data = decrypt_request_body(data=request.data)
        if not status:
            return Response(data=data, status=HTTP_400_BAD_REQUEST)

        serializer = VerifyOTPSerializer(data=data)
        if serializer.is_valid():
            user = request.user
            otp = serializer.validated_data.get("otp")
            otp_obj = UserAccountActivationOTP.objects.filter(user_id=user.id, otp=otp).first()
            if not otp_obj:
                return Response(data="Invalid OTP", status=HTTP_400_BAD_REQUEST)

            if otp_obj.expires < now():
                send_otp_for_verification(user_id=user.id, email=user.email)
                return Response(data="OTP has expired, another has been sent to your email",
                                status=HTTP_400_BAD_REQUEST)

            otp_obj.delete()
            user.is_account_verified = True
            user.save(update_fields=["is_account_verified"])
            return Response(status=HTTP_201_CREATED)
        return Response(data=dict(errors=serializer.errors), status=HTTP_400_BAD_REQUEST)
from django.urls import path

from .api_views import SignInAPIView, SignUpAPIView, VerifyOTPAPIView

app_name = "account"
urlpatterns = [
    path("sign-up/", SignUpAPIView.as_view(), name="sign_up"),
    path("sign-in/", SignInAPIView.as_view(), name="sign_in"),
    path("verify-otp/", VerifyOTPAPIView.as_view(), name="verify_otp"),
]
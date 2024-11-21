from hashlib import sha256
import json

from decouple import config
from django.contrib.auth.hashers import make_password
from django.utils.timezone import now
from django.test import TestCase
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED
from rest_framework.test import APIClient


from account.models import User, UserAccountActivationOTP
from django.utils.timezone import now, timedelta

class APITestSetup(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.signup_url = reverse('account:sign_up')
        self.signin_url = reverse('account:sign_in')
        self.verify_otp_url = reverse('account:verify_otp')

        self.valid_user_data = {
            "email": "testuser@example.com",
            "password": "Password@1"
        }
        self.valid_signin_data = {
            "email": "testuser@example.com",
            "password": "Password@1"
        }
        nowd = str(now())
        self.headers = {
            'API-KEY': config("API_KEY", cast=str),
            'HASH-KEY': sha256(
                (config("API_KEY", cast=str) + config("SECRET_KEY", cast=str) + nowd).encode()).hexdigest(),
            'IDEMPOTENCY-KEY': nowd,
        }



class TestSignUpAPIView(APITestSetup):
    def test_signup_success(self):
        response = self.client.post(
            self.signup_url,
            data=json.dumps(self.valid_user_data),
            content_type='application/json',
            headers=self.headers
        )
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)

    def test_signup_invalid_email(self):
        invalid_data = {**self.valid_user_data, "email": "invalid-email"}
        response = self.client.post(
            self.signup_url,
            data=json.dumps(invalid_data),
            content_type='application/json',
            headers=self.headers
        )
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("errors", response.data)

    def test_signup_existing_email(self):
        User.objects.create(email="testuser@example.com", password=make_password("Password@1"))
        response = self.client.post(
            self.signup_url,
            data=json.dumps(self.valid_user_data),
            content_type='application/json',
            headers=self.headers
        )
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("errors", response.data)


class TestSignInAPIView(APITestSetup):
    def setUp(self):
        super().setUp()
        self.user = User.objects.create(
            email="testuser@example.com", password=make_password("Password@1"), is_account_verified=True
        )

    def test_signin_success(self):
        response = self.client.post(
            self.signin_url,
            data=json.dumps(self.valid_signin_data),
            content_type='application/json',
            headers=self.headers
        )
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertIn('access_token', response.data['token'])
        self.assertIn('refresh_token', response.data['token'])

    def test_signin_invalid_credentials(self):
        invalid_data = {**self.valid_signin_data, "password": "wrongpassword"}
        response = self.client.post(
            self.signin_url,
            data=json.dumps(invalid_data),
            content_type='application/json',
            headers=self.headers
        )
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("errors", response.data)

    def test_signin_unverified_account(self):
        self.user.is_account_verified = False
        self.user.save()
        response = self.client.post(
            self.signin_url,
            data=json.dumps(self.valid_signin_data),
            content_type='application/json',
            headers=self.headers
        )
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertFalse(response.data["is_account_verified"])


class TestVerifyOTPAPIView(APITestSetup):
    def setUp(self):
        super().setUp()
        self.user = User.objects.create(
            email="testuser@example.com", password=make_password("Password@1"), is_account_verified=False
        )
        self.otp = UserAccountActivationOTP.objects.create(
            user=self.user,
            otp="123456",
            expires=now() + timedelta(minutes=10)
        )
        self.client.force_authenticate(user=self.user)

    def test_verify_otp_success(self):
        data = {"otp": "123456"}
        response = self.client.post(
            self.verify_otp_url,
            data=json.dumps(data),
            content_type='application/json',
            headers=self.headers
        )
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_account_verified)

    def test_verify_otp_invalid_otp(self):
        data = {"otp": "999999"}
        response = self.client.post(
            self.verify_otp_url,
            data=json.dumps(data),
            content_type='application/json',
            headers=self.headers
        )
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, "Invalid OTP")

    def test_verify_otp_expired(self):
        self.otp.expires = now() - timedelta(minutes=1)
        self.otp.save()
        data = {"otp": "123456"}
        response = self.client.post(
            self.verify_otp_url,
            data=json.dumps(data),
            content_type='application/json',
            headers=self.headers
        )
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("OTP has expired", response.data)


class TestIntegrationWorkflow(APITestSetup):
    def test_signup_signin_verify_otp_workflow(self):
        signup_response = self.client.post(
            self.signup_url,
            data=json.dumps(self.valid_user_data),
            content_type='application/json',
            headers=self.headers
        )
        self.assertEqual(signup_response.status_code, HTTP_201_CREATED)

        user = User.objects.get(email=self.valid_user_data["email"])
        otp = UserAccountActivationOTP.objects.get(user=user)
        headers = self.headers.copy()
        headers.update({"AUTHORIZATION": f"Bearer {RefreshToken.for_user(user).access_token}"})

        otp_response = self.client.post(
            self.verify_otp_url,
            data=json.dumps({"otp": otp.otp}),
            content_type='application/json',
            headers=headers
        )
        self.assertEqual(otp_response.status_code, HTTP_201_CREATED)

        signin_response = self.client.post(
            self.signin_url,
            data=json.dumps(self.valid_signin_data),
            content_type='application/json',
            headers=self.headers
        )
        self.assertEqual(signin_response.status_code, HTTP_201_CREATED)
        self.assertIn('access_token', signin_response.data['token'])

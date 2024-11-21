from hashlib import sha256

from decouple import config
from django.utils.timezone import now
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APITestCase, APIClient
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST

from account.models import User
from catalogue.models import MedicationSKU
from django.urls import reverse


class MedicationAPIViewTests(APITestCase):
    def setUp(self):
        self.medication = MedicationSKU.objects.create(
            medication_name="Paracetamol",
            dose=500,
            presentation="Tablet",
            unit="mg"
        )

        nowd = str(now())

        user = User.objects.create(email="email@email.com", password="Password@1", is_account_verified=True)
        access_token = RefreshToken.for_user(user).access_token

        self.headers = {
            'API-KEY': config("API_KEY", cast=str),
            'HASH-KEY': sha256((config("API_KEY", cast=str) + config("SECRET_KEY", cast=str) + nowd).encode()).hexdigest(),
            'IDEMPOTENCY-KEY': nowd,
            "AUTHORIZATION": f"Bearer {access_token}"
        }

        self.client = APIClient()
        self.create_read_url = reverse("catalogue:medication_sku_create_read")
        self.update_delete_read_url = reverse("catalogue:medication_sku_update_delete_read")


    def test_get_all_medications(self):
        response = self.client.get(self.create_read_url, headers=self.headers)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["medication_name"], "Paracetamol")

    def test_create_medication(self):
        data = {
            "medication_name": "Ibuprofen",
            "dose": 200,
            "presentation": "Tablet",
            "unit": "mg"
        }
        response = self.client.post(self.create_read_url, data, format="json", headers=self.headers)
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertTrue(MedicationSKU.objects.filter(medication_name="Ibuprofen").exists())

    def test_create_medication_invalid_data(self):
        data = {
            "medication_name": "Aspirin",
            "dose": -100,  # Invalid dose
            "presentation": "Tablet",
            "unit": "mg"
        }
        response = self.client.post(self.create_read_url, data, format="json", headers=self.headers)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("errors", response.data)


    def test_get_single_medication(self):
        url = f"{self.update_delete_read_url}?medication_id={self.medication.msku_id}"
        response = self.client.get(url,  headers=self.headers)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data["data"]["medication_name"], "Paracetamol")


    def test_update_medication(self):
        data = {
            "msku_id": self.medication.msku_id,
            "medication_name": "Paracetamol Updated",
            "dose": 650,
            "presentation": "Capsule",
            "unit": "mg"
        }
        response = self.client.patch(self.update_delete_read_url, data, format="json", headers=self.headers)
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.medication.refresh_from_db()
        self.assertEqual(self.medication.medication_name, "Paracetamol Updated")

    def test_update_medication_invalid_data(self):
        data = {
            "msku_id": self.medication.msku_id,
            "medication_name": "Duplicate",
            "dose": -500,  # Invalid dose
            "presentation": "Tablet",
            "unit": "mg"
        }
        response = self.client.patch(self.update_delete_read_url, data, format="json", headers=self.headers)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("errors", response.data)


    def test_delete_medication(self):
        data = {"msku_id": self.medication.msku_id}
        response = self.client.delete(self.update_delete_read_url, data, format="json", headers=self.headers)
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertFalse(MedicationSKU.objects.filter(msku_id=self.medication.msku_id).exists())






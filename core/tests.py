from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase


class BaseAPITestCase(APITestCase):
    register_url = "/api/auth/register/"
    login_url = "/api/auth/login/"
    patients_url = "/api/patients/"
    doctors_url = "/api/doctors/"
    mappings_url = "/api/mappings/"

    def setUp(self):
        self.user_email = "tester@example.com"
        self.user_password = "StrongPass123!"

    def create_user(self):
        User = get_user_model()
        return User.objects.create_user(
            username=self.user_email,
            email=self.user_email,
            first_name="Test User",
            password=self.user_password,
        )

    def register_user_via_api(self):
        payload = {
            "name": "Test User",
            "email": self.user_email,
            "password": self.user_password,
        }
        return self.client.post(self.register_url, payload, format="json")

    def login_and_authenticate(self):
        payload = {
            "email": self.user_email,
            "password": self.user_password,
        }
        resp = self.client.post(self.login_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK, resp.data)
        token = resp.data.get("access")
        self.assertIsNotNone(token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return token

    def create_patient(self):
        payload = {
            "name": "John Doe",
            "age": 30,
            "gender": "Male",
            "contact": "+1-555-0101",
            "address": "NY",
            "medical_history": "Diabetes",
        }
        resp = self.client.post(self.patients_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, resp.data)
        return resp.data["id"], payload

    def create_doctor(self):
        payload = {
            "name": "Dr. Smith",
            "specialization": "Cardiology",
            "email": "drsmith@example.com",
            "phone": "+1-555-0102",
            "hospital": "City Hospital",
            "years_of_experience": 10,
        }
        resp = self.client.post(self.doctors_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, resp.data)
        return resp.data["id"], payload

    def create_mapping(self, patient_id, doctor_id):
        payload = {
            "patient": patient_id,
            "doctor": doctor_id,
        }
        resp = self.client.post(self.mappings_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, resp.data)
        return resp.data["id"]


class AuthRoutesTests(BaseAPITestCase):
    def test_register_route(self):
        resp = self.register_user_via_api()
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["email"], self.user_email)

    def test_login_route_returns_jwt(self):
        self.create_user()
        resp = self.client.post(
            self.login_url,
            {"email": self.user_email, "password": self.user_password},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", resp.data)
        self.assertIn("refresh", resp.data)


class PatientRoutesTests(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.create_user()
        self.login_and_authenticate()

    def test_create_patient(self):
        patient_id, _ = self.create_patient()
        self.assertIsNotNone(patient_id)

    def test_list_patients(self):
        self.create_patient()
        resp = self.client.get(self.patients_url, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)

    def test_get_patient_detail(self):
        patient_id, _ = self.create_patient()
        resp = self.client.get(f"{self.patients_url}{patient_id}/", format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["id"], patient_id)

    def test_update_patient(self):
        patient_id, payload = self.create_patient()
        updated_payload = dict(payload)
        updated_payload["name"] = "John Updated"

        resp = self.client.put(f"{self.patients_url}{patient_id}/", updated_payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["name"], "John Updated")

    def test_delete_patient(self):
        patient_id, _ = self.create_patient()
        resp = self.client.delete(f"{self.patients_url}{patient_id}/", format="json")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class DoctorRoutesTests(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.create_user()
        self.login_and_authenticate()

    def test_create_doctor(self):
        doctor_id, _ = self.create_doctor()
        self.assertIsNotNone(doctor_id)

    def test_list_doctors(self):
        self.create_doctor()
        resp = self.client.get(self.doctors_url, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)

    def test_get_doctor_detail(self):
        doctor_id, _ = self.create_doctor()
        resp = self.client.get(f"{self.doctors_url}{doctor_id}/", format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["id"], doctor_id)

    def test_update_doctor(self):
        doctor_id, payload = self.create_doctor()
        updated_payload = dict(payload)
        updated_payload["name"] = "Dr. Updated"

        resp = self.client.put(f"{self.doctors_url}{doctor_id}/", updated_payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["name"], "Dr. Updated")

    def test_delete_doctor(self):
        doctor_id, _ = self.create_doctor()
        resp = self.client.delete(f"{self.doctors_url}{doctor_id}/", format="json")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class MappingRoutesTests(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.create_user()
        self.login_and_authenticate()

    def test_create_mapping(self):
        patient_id, _ = self.create_patient()
        doctor_id, _ = self.create_doctor()
        mapping_id = self.create_mapping(patient_id, doctor_id)
        self.assertIsNotNone(mapping_id)

    def test_list_mappings(self):
        patient_id, _ = self.create_patient()
        doctor_id, _ = self.create_doctor()
        self.create_mapping(patient_id, doctor_id)

        resp = self.client.get(self.mappings_url, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)

    def test_get_doctors_for_patient(self):
        patient_id, _ = self.create_patient()
        doctor_id, _ = self.create_doctor()
        self.create_mapping(patient_id, doctor_id)

        resp = self.client.get(f"{self.mappings_url}{patient_id}/", format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)

    def test_delete_mapping(self):
        patient_id, _ = self.create_patient()
        doctor_id, _ = self.create_doctor()
        mapping_id = self.create_mapping(patient_id, doctor_id)

        resp = self.client.delete(f"{self.mappings_url}{mapping_id}/", format="json")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
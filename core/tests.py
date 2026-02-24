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
        self.username = "tester"

    def create_user(self):
        User = get_user_model()
        try:
            return User.objects.create_user(
                email=self.user_email,
                password=self.user_password,
                name="Test User",
            )
        except TypeError:
            try:
                return User.objects.create_user(
                    username=self.username,
                    email=self.user_email,
                    password=self.user_password,
                )
            except TypeError:
                return User.objects.create_user(
                    self.username,
                    self.user_email,
                    self.user_password,
                )

    def register_user_via_api(self):
        payloads = [
            {"name": "Test User", "email": self.user_email, "password": self.user_password},
            {"username": self.username, "email": self.user_email, "password": self.user_password},
        ]
        for payload in payloads:
            resp = self.client.post(self.register_url, payload, format="json")
            if resp.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED):
                return resp
        self.fail(f"Register failed for all payloads. Last status={resp.status_code}, body={resp.data}")

    def login_and_authenticate(self):
        payloads = [
            {"email": self.user_email, "password": self.user_password},
            {"username": self.username, "password": self.user_password},
        ]
        last_resp = None
        for payload in payloads:
            resp = self.client.post(self.login_url, payload, format="json")
            last_resp = resp
            if resp.status_code == status.HTTP_200_OK:
                token = resp.data.get("access") or resp.data.get("token")
                if token:
                    self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
                    return token
        self.fail(f"Login failed for all payloads. Last status={last_resp.status_code}, body={last_resp.data}")

    def create_patient(self):
        candidate_payloads = [
            {"name": "John Doe", "age": 30, "gender": "Male", "address": "NY"},
            {"name": "John Doe", "age": 30, "gender": "M", "address": "NY"},
            {"full_name": "John Doe", "age": 30, "gender": "Male"},
            {"name": "John Doe", "dob": "1994-01-01", "gender": "Male"},
        ]
        last_resp = None
        for payload in candidate_payloads:
            resp = self.client.post(self.patients_url, payload, format="json")
            last_resp = resp
            if resp.status_code == status.HTTP_201_CREATED:
                return resp.data.get("id"), payload
        self.fail(f"Patient create failed. Last status={last_resp.status_code}, body={last_resp.data}")

    def create_doctor(self):
        candidate_payloads = [
            {"name": "Dr. Smith", "specialization": "Cardiology", "email": "drsmith@example.com"},
            {"name": "Dr. Smith", "speciality": "Cardiology", "email": "drsmith@example.com"},
            {"name": "Dr. Smith", "specialization": "Cardiology"},
        ]
        last_resp = None
        for payload in candidate_payloads:
            resp = self.client.post(self.doctors_url, payload, format="json")
            last_resp = resp
            if resp.status_code == status.HTTP_201_CREATED:
                return resp.data.get("id"), payload
        self.fail(f"Doctor create failed. Last status={last_resp.status_code}, body={last_resp.data}")

    def create_mapping(self, patient_id, doctor_id):
        candidate_payloads = [
            {"patient": patient_id, "doctor": doctor_id},
            {"patient_id": patient_id, "doctor_id": doctor_id},
        ]
        last_resp = None
        for payload in candidate_payloads:
            resp = self.client.post(self.mappings_url, payload, format="json")
            last_resp = resp
            if resp.status_code == status.HTTP_201_CREATED:
                return resp.data.get("id")
        self.fail(f"Mapping create failed. Last status={last_resp.status_code}, body={last_resp.data}")


class AuthRoutesTests(BaseAPITestCase):
    def test_register_route(self):
        resp = self.register_user_via_api()
        self.assertIn(resp.status_code, (status.HTTP_200_OK, status.HTTP_201_CREATED))

    def test_login_route_returns_jwt(self):
        self.create_user()
        resp = self.client.post(self.login_url, {"email": self.user_email, "password": self.user_password}, format="json")
        if resp.status_code != status.HTTP_200_OK:
            resp = self.client.post(self.login_url, {"username": self.username, "password": self.user_password}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue("access" in resp.data or "token" in resp.data)


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

    def test_get_patient_detail(self):
        patient_id, _ = self.create_patient()
        resp = self.client.get(f"{self.patients_url}{patient_id}/", format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_update_patient(self):
        patient_id, payload = self.create_patient()
        updated = dict(payload)
        if "name" in updated:
            updated["name"] = "John Updated"
        elif "full_name" in updated:
            updated["full_name"] = "John Updated"
        elif "age" in updated and isinstance(updated["age"], int):
            updated["age"] = updated["age"] + 1

        resp = self.client.put(f"{self.patients_url}{patient_id}/", updated, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_delete_patient(self):
        patient_id, _ = self.create_patient()
        resp = self.client.delete(f"{self.patients_url}{patient_id}/", format="json")
        self.assertIn(resp.status_code, (status.HTTP_200_OK, status.HTTP_204_NO_CONTENT))


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

    def test_get_doctor_detail(self):
        doctor_id, _ = self.create_doctor()
        resp = self.client.get(f"{self.doctors_url}{doctor_id}/", format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_update_doctor(self):
        doctor_id, payload = self.create_doctor()
        updated = dict(payload)
        if "name" in updated:
            updated["name"] = "Dr. Updated"

        resp = self.client.put(f"{self.doctors_url}{doctor_id}/", updated, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_delete_doctor(self):
        doctor_id, _ = self.create_doctor()
        resp = self.client.delete(f"{self.doctors_url}{doctor_id}/", format="json")
        self.assertIn(resp.status_code, (status.HTTP_200_OK, status.HTTP_204_NO_CONTENT))


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

    def test_get_doctors_for_patient(self):
        patient_id, _ = self.create_patient()
        doctor_id, _ = self.create_doctor()
        self.create_mapping(patient_id, doctor_id)

        resp = self.client.get(f"{self.mappings_url}{patient_id}/", format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_delete_mapping(self):
        patient_id, _ = self.create_patient()
        doctor_id, _ = self.create_doctor()
        mapping_id = self.create_mapping(patient_id, doctor_id)

        resp = self.client.delete(f"{self.mappings_url}{mapping_id}/", format="json")
        self.assertIn(resp.status_code, (status.HTTP_200_OK, status.HTTP_204_NO_CONTENT))
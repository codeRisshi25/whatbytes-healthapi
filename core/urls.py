from django.urls import path

from .views import (
    DoctorDetailView,
    DoctorListCreateView,
    LoginView,
    MappingByPatientView,
    MappingListCreateView,
    PatientDetailView,
    PatientListCreateView,
    RegisterView,
)

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("patients/", PatientListCreateView.as_view(), name="patients-list-create"),
    path("patients/<int:pk>/", PatientDetailView.as_view(), name="patients-detail"),
    path("doctors/", DoctorListCreateView.as_view(), name="doctors-list-create"),
    path("doctors/<int:pk>/", DoctorDetailView.as_view(), name="doctors-detail"),
    path("mappings/", MappingListCreateView.as_view(), name="mappings-list-create"),
    path("mappings/<int:patient_id>/", MappingByPatientView.as_view(), name="mappings-by-patient"),
]

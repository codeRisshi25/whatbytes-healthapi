from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Doctor, Patient, PatientDoctorMapping
from .serializers import (
    DoctorSerializer,
    LoginSerializer,
    PatientDoctorMappingListSerializer,
    PatientDoctorMappingSerializer,
    PatientSerializer,
    RegisterSerializer,
)


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "id": user.id,
                "name": user.first_name,
                "email": user.email,
                "message": "User registered successfully.",
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class PatientListCreateView(generics.ListCreateAPIView):
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Patient.objects.filter(created_by=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Patient.objects.filter(created_by=self.request.user)


class DoctorListCreateView(generics.ListCreateAPIView):
    queryset = Doctor.objects.all().order_by("-created_at")
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]


class DoctorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]


class MappingListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PatientDoctorMapping.objects.filter(patient__created_by=self.request.user).select_related(
            "patient", "doctor"
        )

    def get_serializer_class(self):
        if self.request.method == "GET":
            return PatientDoctorMappingListSerializer
        return PatientDoctorMappingSerializer

    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)


class MappingByPatientView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, patient_id):
        patient = get_object_or_404(Patient, id=patient_id, created_by=request.user)
        mappings = PatientDoctorMapping.objects.filter(patient=patient).select_related("patient", "doctor")
        serializer = PatientDoctorMappingListSerializer(mappings, many=True)
        return Response(serializer.data)

    def delete(self, request, patient_id):
        mapping = get_object_or_404(PatientDoctorMapping, id=patient_id, patient__created_by=request.user)
        mapping.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



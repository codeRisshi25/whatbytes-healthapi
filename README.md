# Django Assignment 1 - Healthcare Backend

Backend for healthcare management built with Django, Django REST Framework, PostgreSQL, and JWT authentication.

## Tech Stack

- Django
- Django REST Framework
- PostgreSQL
- Simple JWT (`djangorestframework-simplejwt`)
- Docker + Docker Compose

## Setup

1. Copy environment file:
   - `cp .env.example .env`
2. Start the services:
   - `docker compose up --build`
3. API base URL:
   - `http://localhost:8000/api/`
   - `http://localhost:8000/api/`

OpenAPI / Swagger UI:

- `http://localhost:8000/api/docs/`

## Authentication

Use `Authorization: Bearer <access_token>` for protected endpoints.

## API Endpoints

### 1) Authentication

- `POST /api/auth/register/`
  - body:
    ```json
    {
      "name": "John Doe",
      "email": "john@example.com",
      "password": "StrongPass@123"
    }
    ```
- `POST /api/auth/login/`
  - body:
    ```json
    {
      "email": "john@example.com",
      "password": "StrongPass@123"
    }
    ```

### 2) Patients (Authenticated)

- `POST /api/patients/`
- `GET /api/patients/`
- `GET /api/patients/<id>/`
- `PUT /api/patients/<id>/`
- `DELETE /api/patients/<id>/`

Patient body fields:

```json
{
  "name": "Alice",
  "age": 30,
  "gender": "Female",
  "contact": "+1-555-0101",
  "address": "New York",
  "medical_history": "Diabetes"
}
```

### 3) Doctors (Authenticated)

- `POST /api/doctors/`
- `GET /api/doctors/`
- `GET /api/doctors/<id>/`
- `PUT /api/doctors/<id>/`
- `DELETE /api/doctors/<id>/`

Doctor body fields:

```json
{
  "name": "Dr. Smith",
  "specialization": "Cardiology",
  "email": "dr.smith@example.com",
  "phone": "+1-555-0102",
  "hospital": "City Hospital",
  "years_of_experience": 10
}
```

### 4) Patient-Doctor Mapping (Authenticated)

- `POST /api/mappings/`
  - body:
    ```json
    {
      "patient": 1,
      "doctor": 2
    }
    ```
- `GET /api/mappings/`
- `GET /api/mappings/<patient_id>/`
- `DELETE /api/mappings/<id>/`

Note: `GET /api/mappings/<patient_id>/` and `DELETE /api/mappings/<id>/` share the same path pattern and differ by HTTP method.

## Validation and Error Handling

- Serializer-based validation for request payloads
- Password validation using Django password validators
- Ownership validation for patient and mapping operations
- Proper HTTP status codes and DRF validation responses

## Security

- JWT-based authentication
- Environment variables for sensitive settings
- PostgreSQL used as persistent database

## Deploy to Azure

This repo includes a GitHub Actions workflow to build and push the container to Azure Container Registry and update an Azure Web App for Containers.

Required GitHub secrets:
- `AZURE_CREDENTIALS` — service principal JSON for `azure/login` action
- `ACR_NAME` — your Azure Container Registry name (no suffix)
- `IMAGE_NAME` — image repository name (e.g., `whatbytes-web`)
- `AZURE_RESOURCE_GROUP` — Azure resource group for the Web App
- `AZURE_WEBAPP_NAME` — Web App name

Workflow: `.github/workflows/azure-container-deploy.yml` pushes `latest` tag to ACR and updates the Web App to use it. The container runs migrations at startup via `entrypoint.sh`.

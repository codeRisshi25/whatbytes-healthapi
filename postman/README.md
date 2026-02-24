Postman Usage

1. Import the collection `postman/Healthcare.postman_collection.json` into Postman.
2. Create environment with variable `baseUrl` (default: `http://localhost:8000/api`) and `accessToken` (empty).
3. Use `Auth -> Register` to create an account.
4. Use `Auth -> Login` to obtain `access` and `refresh` tokens. Copy the `access` token into the environment `accessToken` variable.
5. Run patient/doctor/mapping requests using the environment.

Notes:
- Protected endpoints require `Authorization: Bearer {{accessToken}}` header.
- Replace `:id` and `:patient_id` in request URLs with actual numeric IDs returned from create/list responses.
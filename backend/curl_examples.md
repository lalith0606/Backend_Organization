# API Usage Examples

## 1. Create Organization
Register a new organization and create the initial admin account.

```bash
curl -X POST "http://localhost:8000/org/create" \
-H "Content-Type: application/json" \
-d '{
  "organization_name": "acme",
  "email": "admin@acme.com",
  "password": "StrongP@ssw0rd"
}'
```

## 2. Admin Login
Login to get a JWT access token.

```bash
curl -X POST "http://localhost:8000/admin/login" \
-H "Content-Type: application/json" \
-d '{
  "email": "admin@acme.com",
  "password": "StrongP@ssw0rd"
}'
```

**Response:**
```json
{
  "access_token": "ey...",
  "token_type": "bearer",
  "expires_in": 3600,
  "admin": { ... }
}
```

## 3. Get Organization
Retrieve organization details (public or authenticated based on implementation).

```bash
curl -X GET "http://localhost:8000/org/get?organization_name=acme"
```

## 4. Update Organization (Rename)
Rename the organization. Migration will happen automatically using the access token from step 2.

```bash
curl -X PUT "http://localhost:8000/org/update" \
-H "Authorization: Bearer <YOUR_ACCESS_TOKEN>" \
-H "Content-Type: application/json" \
-d '{
  "organization_name": "acme",
  "new_organization_name": "acme_global",
  "email": "admin@acme.com", 
  "password": "NewStrongP@ssw0rd"
}'
```

## 5. Delete Organization
Delete the organization and all its data.

```bash
curl -X DELETE "http://localhost:8000/org/delete" \
-H "Authorization: Bearer <YOUR_ACCESS_TOKEN>" \
-H "Content-Type: application/json" \
-d '{
  "organization_name": "acme_global"
}'
```
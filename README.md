# P2P Energy Swap — Backend

This is the backend for the P2P Energy Swap application (Django + Django REST Framework). It provides authentication, 
user registration, and user profile endpoints including JWT token issuance using Simple JWT.

This README is tailored to explains how to set up the project quickly, what endpoints exist, how authentication works,
and how to test everything locally.

---

## Highlights

- Django project with a custom `accounts.User` model.
- Token-based authentication using JSON Web Tokens (Simple JWT).
- Endpoints exposed under `/api/`:
  - `POST /api/token/` — obtain access & refresh tokens
  - `POST /api/token/refresh/` — refresh access token
  - `GET /api/me/` — returns current authenticated user (includes `name` field)
  - `POST /api/register/` — create a new user (email, password, first_name, last_name)
- CORS configured for local development.

---

## Quick setup (local, Linux/macOS)

1. Clone the repo and cd into it:

```bash
git clone <repo> p2p-energy-backend
cd p2p-energy-backend
```

2. Create and activate a Python virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
```

3. Install Python dependencies:

```bash
pip install -r requirements.txt
# If you don't have a requirements.txt, install these:
pip install django djangorestframework djangorestframework-simplejwt django-cors-headers python-dotenv Pillow
```

4. Create a `.env` file in the project root (optional) to override settings used in development. Example `.env`:

```
DJANGO_DEBUG=true
DJANGO_SECRET_KEY=replace-with-a-secret
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
POSTGRES_DB=            # optional
```

5. Run migrations and start the server:

```bash
python manage.py migrate
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/api/`.

---

## Authentication & Endpoints

All API endpoints are under `/api/` because the project `urls.py` includes `path('api/', include('accounts.urls'))`.

- Obtain tokens (Simple JWT):
  - `POST /api/token/` with JSON `{ "email": "user@example.com", "password": "secret" }`.
  - Response: `{ "refresh": "<refresh>", "access": "<access>" }`.
- Refresh access:
  - `POST /api/token/refresh/` with JSON `{ "refresh": "<refresh_token>" }`.
  - Response: `{ "access": "<new_access>" }`.
- Current user:
  - `GET /api/me/` with header `Authorization: Bearer <access_token>`.
  - Response includes `name`, which is derived from `first_name` + `last_name` (falls back to username or email prefix).
- Register:
  - `POST /api/register/` with JSON `{ "email": "new@example.com", "password": "mypwd", "first_name": "Jane", "last_name": "Doe" }`.
  - Response: created user fields (password is write-only).

### curl examples

Obtain tokens:

```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"secret"}'
```

Refresh access:

```bash
curl -X POST http://127.0.0.1:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh":"<refresh_token>"}'
```

Get current user:

```bash
curl http://127.0.0.1:8000/api/me/ \
  -H "Authorization: Bearer <access_token>"
```

Register a user:

```bash
curl -X POST http://127.0.0.1:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"new@example.com","password":"newpass","first_name":"Jane","last_name":"Doe"}'
```

---

## Environment & Settings notes

- `AUTH_USER_MODEL` is `accounts.User` (custom user). The code uses `email` as the login field.
- `REST_FRAMEWORK` in `settings.py` is configured to use `rest_framework_simplejwt.authentication.JWTAuthentication`
- by default.
- `SIMPLE_JWT` settings are present in `settings.py` with sensible lifetimes.
- `CORS_ALLOW_ALL_ORIGINS = True` is enabled for development.

If the frontend uses a different API base path (for example, `/api/auth/`), either change the backend URLs or update
the frontend `VITE_API_BASE_URL` accordingly.

---

## Tests

To run tests:

```bash
python manage.py test
```

(There are currently minimal or no automated tests; adding endpoint tests is recommended for production-readiness.)

---

## Deployment notes (brief)

- Use a secure `DJANGO_SECRET_KEY` in production and set `DEBUG=false`.
- Configure `ALLOWED_HOSTS` with your production domains.
- Use a proper database (Postgres) and static file serving (WhiteNoise / S3) in production.
- Consider rotating/blacklisting refresh tokens if you need stricter token control.

---

## Contact / contributor notes

If you need changes to the API shape (for example persisting a single `name` column instead of `first_name`/`last_name`), I can add a `name` field to the `User` model and wire migrations. I can also add tests and example Postman collections on request.

---
!

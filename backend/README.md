# backend

Minimal FastAPI service the API tests run against. In-memory store, JWT
auth, no DB. Resets on restart.

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

## endpoints

```
GET   /v1/health
POST  /v1/auth/login             -> { access_token, token_type, expires_in }
GET   /v1/tasks?q=&status=&tag=&limit=&offset=
POST  /v1/tasks
GET   /v1/tasks/{id}
PATCH /v1/tasks/{id}
DELETE /v1/tasks/{id}
DELETE /v1/tasks                 # test-only: wipe store
```

All `/v1/tasks*` routes require `Authorization: Bearer <jwt>`.

## demo creds

```
test@taskflow.io / Test123!
```

Override via `DEMO_USER_EMAIL` / `DEMO_USER_PASSWORD` env vars.
JWT secret: `JWT_SECRET` env var (default `dev-secret-change-me`).

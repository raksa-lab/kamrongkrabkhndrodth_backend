# Readwell Book Store API

FastAPI + PostgreSQL backend for the storefront and admin book management.

## Run locally

```powershell
cd 'D:\For Study\Year 4\booking-store\backend'
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
Copy-Item .env.example .env
docker compose up -d postgres
uvicorn app.main:app --reload --port 8000
```

API endpoints:

- `GET /api/health`
- `GET /api/books?search=&category=&availability=&page=&page_size=`
- `GET /api/books/{slug}`
- `POST /api/admin/login` with `{ "email": "...", "password": "..." }`
- Authenticated `GET/POST /api/admin/books`
- Authenticated `PUT/DELETE /api/admin/books/{id}`
- Authenticated `POST /api/admin/upload` using multipart field `file`

On startup, the API creates the tables and seeds the admin account from `ADMIN_EMAIL` and `ADMIN_PASSWORD`. Change both values in `.env` before production. The API has no customer login, cart, checkout, or payment endpoints. Telegram remains the purchase flow.

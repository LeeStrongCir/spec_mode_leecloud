# Quickstart: Console Dashboard Feature

## For Developers

### Running the Application

```bash
cd backend
python3.11 -m venv .venv && source .venv/bin/activate
uv sync --extra dev
```

### Admin Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin@123` |

The admin user is seeded automatically on server startup. No manual database setup required.

### Local Development

```bash
uv run alembic upgrade head
uv run uvicorn src.app.main:app --reload --port 8000
```

Access points:
- **Login**: http://localhost:8000/login
- **Console**: http://localhost:8000/console (redirects to login if not authenticated)

### Testing Console Auth Flow

1. Navigate to `http://localhost:8000/console`
2. You should be redirected to `/login` (unauthenticated access)
3. Enter `admin` / `admin@123`
4. You should be redirected to `/console` dashboard

### Testing Branding Changes

All pages should display "Lee云" instead of "华为云":
- Login page title: "登录 - Lee云"
- Login page logo: "Lee云"
- Login page login title: "Lee账号登录"
- Login page disclaimer: "我们为您提供Lee账号服务..."
- Login page footer: "©2026 Leecloud.com 版权所有"
- Console page title: "控制台 - Lee云"
- Console header: "Lee云 | 控制台"

### Running Tests

```bash
uv run pytest tests/test_console_auth.py tests/test_seed_admin.py tests/test_console_template.py -v
```

## Changes at a Glance

| File | Change |
|------|--------|
| `backend/src/app/main.py` | Add `GET /console` route + `GET /console/` redirect |
| `backend/src/app/api/auth.py` | Change login to redirect instead of JSON response |
| `backend/src/app/api/deps.py` | Add `require_auth` dependency + `RedirectToLogin` exception |
| `backend/src/app/main.py` | Integrate `lifespan` with admin seeding |
| `backend/frontend/templates/console.html` | NEW: Console dashboard template |
| `backend/frontend/templates/login.html` | Rebrand + update form handling |
| `backend/frontend/static/css/console.css` | NEW: Console dashboard styles |
| `backend/frontend/static/css/style.css` | Rebrand tokens + text |
| `alembic/versions/` | (No migration needed — seed at runtime via lifespan) |

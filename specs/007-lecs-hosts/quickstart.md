# Quick Start: LECS Host Management (007-lecs-hosts)

## Local Development

### Prerequisites

- Python 3.11+
- uv (package manager)
- Git

### Setup

```bash
# From project root
cd backend

# Install dependencies (includes new LECS Host model/deps — no new packages needed)
cd /mnt/d/project_workspace/spec_mode_leecloud/backend && uv sync

# Set up environment variables
cp .env.example .env  # If .env.example exists, otherwise create .env manually
# Ensure DATABASE_URL uses aiosqlite for local dev
# e.g., DATABASE_URL="sqlite+aiosqlite:///./dev.db"

# Run database migrations
cd /mnt/d/project_workspace/spec_mode_leecloud/backend && alembic upgrade head
```

### Run Server

```bash
cd /mnt/d/project_workspace/spec_mode_leecloud/backend
uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
```

Server starts at `http://localhost:8000`.

- Console: `http://localhost:8000/console` (requires login)
- LECS Host List: `http://localhost:8000/console/lecs-hosts/list`
- LECS Host Create: `http://localhost:8000/console/lecs-hosts/create`
- API: `http://localhost:8000/api/v1/lecs-hosts`

### Running Tests

```bash
cd /mnt/d/project_workspace/spec_mode_leecloud/backend

# Unit tests only
pytest tests/unit/test_lecs_host_service.py -v

# Integration tests only
pytest tests/integration/test_lecs_host_api.py -v

# All LECS tests
pytest tests/ -k lecs_host -v

# Full test suite with coverage
pytest --cov=src/app --cov-fail-under=90
```

### Code Style

```bash
cd /mnt/d/project_workspace/spec_mode_leecloud/backend
ruff check src/app tests  # Linting
ruff format src/app tests  # Formatting
```

## Key Files Modified/Added

| File | Status | Purpose |
|------|--------|---------|
| `backend/src/app/models/lecs_host.py` | NEW | LECSHost model + enums |
| `backend/src/app/models/instance_type.py` | NEW | InstanceType + InstanceSpec + OSImage models |
| `backend/src/app/schemas/lecs_host.py` | NEW | Pydantic request/response schemas |
| `backend/src/app/services/lecs_host_service.py` | NEW | Business logic service |
| `backend/src/app/api/lecs_host.py` | NEW | REST API endpoints |
| `backend/src/app/main.py` | MODIFIED | Register lecs_host router + SSR page routes |
| `backend/frontend/templates/lecs_host_list.html` | NEW | List page template |
| `backend/frontend/templates/lecs_host_create.html` | NEW | Creation page template |
| `backend/frontend/static/css/console.css` | MODIFIED | LECS Host specific styles |
| `backend/tests/unit/test_lecs_host_service.py` | NEW | Unit tests |
| `backend/tests/integration/test_lecs_host_api.py` | NEW | Integration tests |
| `backend/tests/e2e/test_lecs_host_list.py` | NEW | Playwright E2E tests |
| `backend/alembic/versions/` | NEW | Migration: add lecs_hosts, instance_types, instance_specs, os_images tables |

## Default Credentials (Dev)

The admin account is seeded at startup via the existing `lifespan` function:

- Username: `admin`
- Password: `admin@123`

Login at `http://localhost:8000/login`, then navigate to Console → search "LECS主机" → LECS Host List.

## API Quick Test

```bash
# Login first
curl -X POST http://localhost:8000/api/auth/login \
  -d "username=admin" -d "password=admin@123" \
  -c cookies.txt -v

# List hosts (empty initially)
curl -b cookies.txt http://localhost:8000/api/v1/lecs-hosts

# Get instance types
curl -b cookies.txt http://localhost:8000/api/v1/instance-types

# Get OS images
curl -b cookies.txt http://localhost:8000/api/v1/os-images
```

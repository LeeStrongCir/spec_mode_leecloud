# Quickstart: LECS Hosts Management

**Date**: 2026-05-09
**Feature**: 007-lecs-hosts

## Prerequisites

- Python 3.11+
- Working virtual environment (see `backend/README.md`)
- Database migrations up to date

## Setup

### 1. Navigate to backend directory

```bash
cd backend
```

### 2. Install dependencies (if not already)

```bash
uv sync --extra dev
```

### 3. Run database migration

```bash
uv run alembic upgrade head
```

This creates the `lecs_hosts` table with all columns defined in the migration.

### 4. Start the server

```bash
uv run uvicorn src.app.main:app --reload --port 8000
```

### 5. Access the pages

- **API documentation**: http://localhost:8000/docs
- **Console** (search for "LECS主机"): http://localhost:8000/console-full
- **LECS Host list page**: http://localhost:8000/console/lecs-hosts/list
- **LECS Host create page**: http://localhost:8000/console/lecs-hosts/create

### 6. Verify via API

```bash
# List hosts (requires valid access_token cookie)
curl -b "access_token=<your_token>" http://localhost:8000/api/v1/lecs-hosts

# Create a host
curl -X POST -b "access_token=<your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "hostname": "test-host-01",
    "billing_mode": "subscription",
    "instance_type": "economy",
    "spec_id": "eco-2c4g",
    "os_image": "huawei_euler",
    "ip_mode": "dhcp",
    "ip_address": null,
    "ip_mask": null,
    "username": "root_admin",
    "password": "MyStr0ng!Pass",
    "duration": 1
  }' \
  http://localhost:8000/api/v1/lecs-hosts

# Get pricing info
curl -b "access_token=<your_token>" http://localhost:8000/api/v1/lecs-hosts/pricing

# Shutdown a host
curl -X POST -b "access_token=<your_token>" \
  http://localhost:8000/api/v1/lecs-hosts/<host_id>/shutdown

# Start a host
curl -X POST -b "access_token=<your_token>" \
  http://localhost:8000/api/v1/lecs-hosts/<host_id>/start

# Delete a host (must be stopped or failed)
curl -X DELETE -b "access_token=<your_token>" \
  http://localhost:8000/api/v1/lecs-hosts/<host_id>
```

## Run Tests

```bash
# Unit + integration tests
cd backend
.venv/bin/python -m pytest tests/test_lecs_host* -v --cov=src/app --cov-report=html
```

## Verification Checklist

After setup, verify the following:

- [ ] User can search "LECS" in console search bar and see "LECS主机" result
- [ ] Clicking search result navigates to `/console/lecs-hosts/list`
- [ ] List page loads (shows empty table for new users)
- [ ] Clicking "创建ECS主机" navigates to creation page
- [ ] Creation form validates hostname, username, password, IP input
- [ ] Selecting a spec updates the cost display in real time
- [ ] Clicking "立即购买" shows confirmation dialog with full summary
- [ ] After submission, new host appears with "创建中" status
- [ ] After ~30s, host status changes to "正常"
- [ ] Shutdown button works on "正常" state host (status: 关机中 → 已关机)
- [ ] Start button works on "已关机" state host (status: 启动中 → 正常)
- [ ] Delete button is disabled for "正常" state; enabled for "已关机"
- [ ] Soft-deleted hosts disappear from the list
- [ ] All interactive components have `data-testid` attributes

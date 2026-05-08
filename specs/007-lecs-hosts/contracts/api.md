# API Contract: LECS Host Service

**Base Path**: `/api/v1/lecs-hosts`
**Auth**: JWT Cookie (`access_token`) — all endpoints require authentication.
**CSRF**: Protected for POST/DELETE operations.
**Rate Limit**: 20 requests/minute per user.

---

## GET /api/v1/lecs-hosts

**Description**: Paginated list of user's hosts (filtered: `deleted_at IS NULL`).

**Query Parameters**:
| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `page` | int | No | 1 | Page number (1-indexed) |
| `page_size` | int | No | 20 | Items per page (max 100) |

**Response (200 OK)**:
```json
{
  "status": "success",
  "data": {
    "items": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "hostname": "web-server-01",
        "billing_mode": "subscription",
        "instance_type": "economy",
        "spec_id": "eco-2c4g",
        "vcpu": 2,
        "ram_gb": 4,
        "system_disk_gb": 40,
        "os_image": "huawei_euler",
        "ip_mode": "dhcp",
        "ip_address": "10.0.0.15",
        "status": "normal",
        "error_msg": null,
        "created_at": "2026-05-09T08:00:00Z",
        "updated_at": "2026-05-09T08:02:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 20,
    "total_pages": 1
  }
}
```

**Authorization**: 
- Regular users: see only their own hosts (`WHERE user_id = current_user.id`)
- Admin users: see all hosts

**Errors**:
| Status | Body | Condition |
|--------|------|-----------|
| 401 | `{"status":"error","error_code":"MISSING_TOKEN","message":"未登录"}` | No valid access_token cookie |

---

## POST /api/v1/lecs-hosts

**Description**: Create a new LECS host (async). Returns immediately with `creating` status.

**Request Body**:
```json
{
  "hostname": "web-server-01",
  "billing_mode": "subscription",
  "instance_type": "economy",
  "spec_id": "eco-2c4g",
  "os_image": "huawei_euler",
  "ip_mode": "dhcp",
  "ip_address": null,
  "ip_mask": null,
  "username": "root_admin",
  "password": "MyStr0ng!Pass",
  "duration": 6
}
```

| Field | Type | Required | Validation |
|-------|------|----------|-----------|
| `hostname` | string | Yes | `^[\w]{4,10}$`, not starting with `_`, unique per user |
| `billing_mode` | string | Yes | `"subscription"` or `"on_demand"` |
| `instance_type` | string | Yes | `"economy"` or `"high_performance"` |
| `spec_id` | string | Yes | Must be valid per instance_type |
| `os_image` | string | Yes | `"huawei_euler"`, `"ubuntu"`, `"windows"` |
| `ip_mode` | string | Yes | `"dhcp"` or `"manual"` |
| `ip_address` | string | Conditional | Required if `ip_mode="manual"`, valid IPv4 |
| `ip_mask` | int | Conditional | Required if `ip_mode="manual"`, 8–24 |
| `username` | string | Yes | `^[a-zA-Z0-9_@.+-]{4,16}$` |
| `password` | string | Yes | `^[a-zA-Z0-9_@#$%^&+=!-]{8,32}$` |
| `duration` | int | Yes | 1–9, 12, or 24 |

**Response (201 Created)**:
```json
{
  "status": "success",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "hostname": "web-server-01",
    "status": "creating",
    "message": "任务已提交"
  }
}
```

**Errors**:
| Status | Body | Condition |
|--------|------|-----------|
| 400 | `{"status":"error","message":"主机名已存在"}` | Hostname already used by user |
| 403 | `{"status":"error","error_code":"QUOTA_EXCEEDED","message":"主机数量达到上限"}` | User has 100+ non-deleted hosts |
| 422 | `{"detail": [...]}` | Validation error on any field |
| 500 | `{"status":"error","message":"服务内部错误"}` | Server error during task creation |

---

## POST /api/v1/lecs-hosts/{id}/shutdown

**Description**: Shutdown a running host (async). ~10s duration.

**Path Parameters**: `id` (UUID)

**Precondition**: Host status must be `normal`.

**Response (200 OK)**:
```json
{
  "status": "success",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "shutting_down",
    "message": "关机指令已下发"
  }
}
```

**Errors**:
| Status | Body | Condition |
|--------|------|-----------|
| 404 | `{"status":"error","message":"主机不存在"}` | Host not found or not owned by user |
| 409 | `{"status":"error","error_code":"INVALID_STATE","message":"仅可对运行中的主机执行关机操作"}` | Host not in `normal` state |

---

## POST /api/v1/lecs-hosts/{id}/start

**Description**: Start a stopped or failed host (async). ~10s duration.

**Path Parameters**: `id` (UUID)

**Precondition**: Host status must be `stopped` or `failed`.

**Response (200 OK)**:
```json
{
  "status": "success",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "starting",
    "message": "启动指令已下发"
  }
}
```

**Errors**:
| Status | Body | Condition |
|--------|------|-----------|
| 404 | `{"status":"error","message":"主机不存在"}` | Host not found or not owned by user |
| 409 | `{"status":"error","error_code":"INVALID_STATE","message":"仅可对已关机或创建失败的主机执行启动操作"}` | Host not in `stopped` or `failed` state |

---

## DELETE /api/v1/lecs-hosts/{id}

**Description**: Soft delete a host (async). Allowed only for `stopped` or `failed` hosts. ~5s duration.

**Path Parameters**: `id` (UUID)

**Precondition**: Host status must be `stopped` or `failed`.

**Response (202 Accepted)**:
```json
{
  "status": "success",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "deleting",
    "message": "删除中，请等待处理完成"
  }
}
```

**Errors**:
| Status | Body | Condition |
|--------|------|-----------|
| 404 | `{"status":"error","message":"主机不存在"}` | Host not found or not owned by user |
| 403 | `{"status":"error","error_code":"NOT_STOPPED","message":"仅支持对已关机或创建失败的主机执行删除"}` | Host in `normal`, `creating`, or transitional state |

---

## GET /api/v1/lecs-hosts/pricing

**Description**: Return current instance spec pricing data.

**Response (200 OK)**:
```json
{
  "status": "success",
  "data": {
    "economy": [
      {"spec_id": "eco-2c2g", "name": "通用计算机", "vcpu": 2, "ram_gb": 2, "system_disk_gb": 40, "monthly_price": 100},
      {"spec_id": "eco-2c4g", "name": "通用计算机", "vcpu": 2, "ram_gb": 4, "system_disk_gb": 40, "monthly_price": 140},
      {"spec_id": "eco-2c8g", "name": "通用计算机", "vcpu": 2, "ram_gb": 8, "system_disk_gb": 40, "monthly_price": 180},
      {"spec_id": "eco-4c8g", "name": "通用计算机", "vcpu": 4, "ram_gb": 8, "system_disk_gb": 40, "monthly_price": 240}
    ],
    "high_performance": [
      {"spec_id": "perf-2c4g", "name": "通用增强计算机", "vcpu": 2, "ram_gb": 4, "system_disk_gb": 40, "monthly_price": 160},
      {"spec_id": "perf-2c8g", "name": "通用增强计算机", "vcpu": 2, "ram_gb": 8, "system_disk_gb": 40, "monthly_price": 200},
      {"spec_id": "perf-4c8g", "name": "通用增强计算机", "vcpu": 4, "ram_gb": 8, "system_disk_gb": 40, "monthly_price": 260},
      {"spec_id": "perf-8c16g", "name": "通用增强计算机", "vcpu": 8, "ram_gb": 16, "system_disk_gb": 40, "monthly_price": 500}
    ]
  }
}
```

---

## Shared Error Response Format

All error responses follow this structure:

```json
{
  "status": "error",
  "error_code": "VALIDATION_ERROR",
  "message": "Human-readable error description"
}
```

| error_code | Meaning |
|------------|---------|
| `MISSING_TOKEN` | No valid auth token |
| `QUOTA_EXCEEDED` | User has reached 100 host limit |
| `INVALID_STATE` | Lifecycle operation not allowed for current host state |
| `NOT_STOPPED` | Delete attempted on a non-stopped/failed host |
| `VALIDATION_ERROR` | Request body validation failed |
| `HOST_NOT_FOUND` | Host ID does not exist for current user |

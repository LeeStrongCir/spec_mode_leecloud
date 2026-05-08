# LECS Host API Contract

## Overview

REST API for LECS Host (cloud server) management. All endpoints require JWT authentication via httpOnly cookies.

**Base path**: `/api/v1/lecs-hosts`  
**Authentication**: JWT Cookie (access_token)  
**Response format**: JSON

---

## GET /api/v1/lecs-hosts

List LECS Host instances for the authenticated user.

### Request

**Method**: `GET`  
**Auth**: Required (JWT httpOnly Cookie)

**Query Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `page` | integer | No | 1 | Page number (min: 1) |
| `page_size` | integer | No | 20 | Items per page (max: 100) |
| `region` | string | No | - | Filter by region (e.g., "华北-北京四") |
| `status` | string | No | - | Filter by status: `creating`, `running`, `stopped`, `error` |
| `search` | string | No | - | Fuzzy match on host name or ID |

### Response (200)

```json
{
  "status": "success",
  "data": {
    "items": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "web-server-01",
        "status": "running",
        "region": "华北-北京四",
        "instance_type": "x1",
        "os_name": "Huawei Cloud EulerOS",
        "public_ip": "1.2.3.4",
        "private_ip": "10.0.0.5",
        "billing_mode": "monthly",
        "tags": [],
        "created_at": "2026-05-01T08:00:00Z",
        "expire_at": "2027-05-01T08:00:00Z"
      }
    ],
    "pagination": {
      "total": 48,
      "page": 1,
      "page_size": 20,
      "pages": 3
    }
  }
}
```

### Errors

| Status | Code | Condition |
|--------|------|-----------|
| 401 | UNAUTHORIZED | Missing or expired JWT token |

---

## POST /api/v1/lecs-hosts

Create a new LECS Host instance.

### Request

**Method**: `POST`  
**Auth**: Required (JWT httpOnly Cookie)  
**Content-Type**: `application/json`

**Body**:

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `name` | string | No | max 64 chars | Host display name |
| `region` | string | Yes | must be valid region | Deployment region |
| `billing_mode` | string | Yes | enum: `monthly`, `hourly` | Billing model |
| `duration` | integer | Conditional | 1-36, required if billing_mode=monthly | Months (for prepaid) |
| `instance_type_id` | string | Yes | must exist | e.g., "x1" |
| `instance_spec_id` | string | Yes | must exist and match instance_type_id | Concrete spec |
| `os_image_id` | string | Yes | must exist and be available | OS template |
| `enable_public_ip` | boolean | No | default: true | Assign public IP |
| `bandwidth_billing_mode` | string | Conditional | enum: `bandwidth`, `traffic`, required if enable_public_ip | Bandwidth billing |
| `bandwidth_mbps` | integer | Conditional | 1-2000, required if enable_public_ip | Bandwidth size |
| `quantity` | integer | Yes | 1-100 | Number of hosts to create |
| `enable_security` | boolean | No | default: true | Host security protection |
| `auto_renew` | boolean | No | default: false | Auto-renewal (prepaid only) |

**Example Request Body**:

```json
{
  "name": "web-server-01",
  "region": "华北-北京四",
  "billing_mode": "monthly",
  "duration": 12,
  "instance_type_id": "x1",
  "instance_spec_id": "x1.2u.2g",
  "os_image_id": "huawei-euler-os-2.0",
  "enable_public_ip": true,
  "bandwidth_billing_mode": "bandwidth",
  "bandwidth_mbps": 5,
  "quantity": 1,
  "enable_security": true,
  "auto_renew": false
}
```

### Response (201)

```json
{
  "status": "success",
  "data": {
    "host_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "web-server-01",
    "status": "creating",
    "price_amount": 1290.00,
    "total_price": 1290.00
  }
}
```

### Errors

| Status | Code | Condition |
|--------|------|-----------|
| 400 | BAD_REQUEST | Validation error (e.g., `{"details": [{"loc": ["body", "quantity"], "msg": "一次最多可以创建100台云服务器"}]}`) |
| 401 | UNAUTHORIZED | Missing or expired JWT token |
| 409 | QUOTA_EXCEEDED | Total host count would exceed 200 |
| 409 | INSUFFICIENT_RESOURCES | Public IP or bandwidth resources unavailable |
| 500 | INTERNAL_ERROR | Provisioning backend returned error |

---

## DELETE /api/v1/lecs-hosts/{host_id}

Soft-delete an existing LECS Host instance (moves to Recycle Bin).

### Request

**Method**: `DELETE`  
**Auth**: Required (JWT httpOnly Cookie)  
**Path Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `host_id` | UUID | Yes | The host ID to delete |

### Response (200)

```json
{
  "status": "success",
  "data": {
    "host_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

### Errors

| Status | Code | Condition |
|--------|------|-----------|
| 401 | UNAUTHORIZED | Missing or expired JWT token |
| 403 | FORBIDDEN | Host belongs to another user |
| 404 | NOT_FOUND | Host ID does not exist or already deleted |
| 409 | CONFLICT | Host is currently running (must be stopped first — future scope) |

---

## Instance Types Catalog

### GET /api/v1/instance-types

List available instance types for the creation page.

### Response (200)

```json
{
  "status": "success",
  "data": {
    "categories": {
      "economy": {
        "label": "经济型",
        "description": "...",
        "specs": [
          {
            "id": "x1.2u.2g",
            "instance_type_id": "x1",
            "vcpus": 2,
            "memory_gib": 2,
            "system_disk_type": "通用型SSD",
            "system_disk_gib": 40,
            "monthly_price": 109.00,
            "is_available": true
          }
        ]
      },
      "high_cost_performance": {
        "label": "高性价比型",
        "description": "...",
        "specs": [...]
      },
      "high_performance": {
        "label": "高性能型",
        "description": "...",
        "specs": [...]
      }
    }
  }
}
```

---

## OS Images Catalog

### GET /api/v1/os-images

List available OS images for the creation page.

### Response (200)

```json
{
  "status": "success",
  "data": {
    "images": [
      {
        "id": "huawei-euler-os-2.0",
        "name": "Huawei Cloud EulerOS",
        "family": "Linux",
        "version": "2.0 标准版 64位",
        "arch": "x86_64",
        "default_disk_gib": 10,
        "is_available": true
      },
      {
        "id": "centos-7",
        "name": "CentOS",
        "family": "Linux",
        "version": "7.9 64位",
        "arch": "x86_64",
        "default_disk_gib": 10,
        "is_available": true
      }
    ]
  }
}
```

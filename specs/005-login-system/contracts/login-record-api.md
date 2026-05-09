# Login Record Query API Contracts

**Feature**: 005-login-system  
**Date**: 2026-05-06

---

## GET /api/auth/login-history

**Description**: 用户查看自己的登录历史记录

**Headers**:
- Cookie: `access_token=<jwt>`

**Query Parameters**:
| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `page` | integer | No | 1 | 页码 |
| `page_size` | integer | No | 10 | 每页记录数 (max 50) |
| `status` | string | No | all | 筛选: `success` / `failed` / `all` |

**Response 200 OK**:
```json
{
  "status": "success",
  "data": {
    "records": [
      {
        "id": "r1-record-uuid",
        "login_time": "2026-05-06T10:30:00Z",
        "ip_address_masked": "192.168.●.●",
        "device_type": "desktop",
        "browser": "Chrome 120",
        "operating_system": "Windows 11",
        "status": "success",
        "is_anomalous": false
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 10,
      "total": 45,
      "total_pages": 5
    }
  }
}
```

**Response 401 Unauthorized**:
```json
{
  "status": "error",
  "error_code": "NOT_AUTHENTICATED",
  "message": "请先登录"
}
```

**Security Notes**:
- 用户只能查看自己的登录记录 (FR-012)
- IP 地址部分脱敏展示 (FR-018)
- 按 login_time 倒序排列 (FR-013)
- 分页默认 10 条/页 (FR-013)

---

## GET /api/admin/login-records

**Description**: 管理员查看全体用户登录记录

**Headers**:
- Cookie: `access_token=<jwt>`
- 需要管理员权限

**Headers**:
- Cookie: `access_token=<jwt>` (需要管理员权限)

**Query Parameters**:
| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `page` | integer | No | 1 | 页码 |
| `page_size` | integer | No | 20 | 每页记录数 (max 100) |
| `user_id` | UUID | No | - | 按用户筛选 |
| `username` | string | No | - | 按用户名筛选 |
| `email` | string | No | - | 按邮箱筛选 |
| `start_time` | datetime | No | - | 起始时间 (ISO 8601) |
| `end_time` | datetime | No | - | 结束时间 (ISO 8601) |
| `status` | string | No | all | 筛选: `success` / `failed` / `all` |
| `ip_address` | string | No | - | 按 IP 地址筛选 |
| `is_anomalous` | boolean | No | - | 仅异常登录记录 |

**Response 200 OK**:
```json
{
  "status": "success",
  "data": {
    "records": [
      {
        "id": "r1-record-uuid",
        "user_id": "u1-user-uuid",
        "username": "zhangsan",
        "email": "zhangsan@example.com",
        "login_time": "2026-05-06T10:30:00Z",
        "ip_address": "192.168.1.100",
        "ip_geo_location": "上海市, 中国",
        "device_type": "desktop",
        "browser": "Chrome 120",
        "operating_system": "Windows 11",
        "status": "success",
        "failure_reason": null,
        "is_anomalous": false
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 1500,
      "total_pages": 75
    }
  }
}
```

**Response 401 Unauthorized**:
```json
{
  "status": "error",
  "error_code": "NOT_AUTHENTICATED",
  "message": "请先登录"
}
```

**Response 403 Forbidden** (非管理员):
```json
{
  "status": "error",
  "error_code": "INSUFFICIENT_PERMISSIONS",
  "message": "管理员权限不足"
}
```

**Response 400 Bad Request** (参数无效):
```json
{
  "status": "error",
  "error_code": "INVALID_PARAMETERS",
  "message": "start_time 必须在 end_time 之前",
  "details": [
    {
      "field": "start_time",
      "error": "Invalid ISO 8601 format"
    }
  ]
}
```

**Security Notes**:
- 仅管理员可访问 (FR-014, FR-015)
- 支持多维度组合筛选：用户、时间范围、IP、登录结果 (FR-015)
- 返回完整 IP 地址（管理员视角，不脱敏）
- 多个筛选条件为 AND 逻辑 (交集筛选)
- 按 login_time 倒序排列

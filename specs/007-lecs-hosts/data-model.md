# Data Model: LECS Hosts

**Date**: 2026-05-09
**Feature**: 007-lecs-hosts

## Entities

### LECSHost

A virtual computing instance representing a cloud server.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK, auto-generated | Unique host identifier |
| `user_id` | UUID | FK → users.id, INDEX, NOT NULL | Owner of the host |
| `hostname` | String(64) | NOT NULL | User-defined host name |
| `billing_mode` | String(16) | NOT NULL | `"subscription"` or `"on_demand"` |
| `instance_type` | String(32) | NOT NULL | `"economy"` or `"high_performance"` |
| `spec_id` | String(32) | NOT NULL | Specific spec identifier (e.g., `"eco-2c2g"`) |
| `vcpu` | Integer | NOT NULL | CPU cores count |
| `ram_gb` | Integer | NOT NULL | Memory in GiB |
| `system_disk_gb` | Integer | NOT NULL | System disk size in GB |
| `os_image` | String(32) | NOT NULL | `"huawei_euler"`, `"ubuntu"`, `"windows"` |
| `ip_mode` | String(16) | NOT NULL | `"dhcp"` or `"manual"` |
| `ip_address` | String(45) | Nullable | IP for manual config; NULL for DHCP |
| `ip_mask` | Integer | Nullable | Subnet mask (8–24); NULL for DHCP |
| `status` | Enum | NOT NULL, default=`creating` | See status machine below |
| `error_msg` | Text | Nullable | Error details on failure |
| `duration` | Integer | NOT NULL | Purchase duration in months (1–9, 12, 24) |
| `unit_price` | Float | NOT NULL | Price per month (CNY) |
| `cost_info` | JSON | Nullable | Snapshot: `{billing_mode, unit_price, duration, total, currency}` |
| `username` | String(64) | NOT NULL | Access credential username |
| `password_hash` | String(255) | NOT NULL | Hashed access credential password |
| `deleted_at` | DateTime | Nullable, INDEX | Soft-delete timestamp (NULL = active) |
| `created_at` | DateTime | NOT NULL, auto-set | Creation timestamp |
| `updated_at` | DateTime | NOT NULL, auto-set | Last update timestamp |

**Indexes**:
- `ix_lecs_hosts_user_id` — for user-scoped queries
- `ix_lecs_hosts_deleted_at` — for soft-delete filtering (`WHERE deleted_at IS NULL`)
- Composite: `(user_id, deleted_at)` — for quota counting

### InstanceSpec (Constant Reference Data)

Not a DB model — defined as a constant in code. Maps spec_id to vCPU, RAM, disk, and price.

| spec_id | instance_type | name | vcpu | ram_gb | disk_gb | monthly_price |
|---------|--------------|------|------|--------|---------|---------------|
| `eco-2c2g` | economy | 通用计算机 | 2 | 2 | 40 | 100 |
| `eco-2c4g` | economy | 通用计算机 | 2 | 4 | 40 | 140 |
| `eco-2c8g` | economy | 通用计算机 | 2 | 8 | 40 | 180 |
| `eco-4c8g` | economy | 通用计算机 | 4 | 8 | 40 | 240 |
| `perf-2c4g` | high_performance | 通用增强计算机 | 2 | 4 | 40 | 160 |
| `perf-2c8g` | high_performance | 通用增强计算机 | 2 | 8 | 40 | 200 |
| `perf-4c8g` | high_performance | 通用增强计算机 | 4 | 8 | 40 | 260 |
| `perf-8c16g` | high_performance | 通用增强计算机 | 8 | 16 | 40 | 500 |

### HostStatus Enum

```python
class HostStatus(str, enum.Enum):
    creating = "creating"
    normal = "normal"
    failed = "failed"
    shutting_down = "shutting_down"
    stopped = "stopped"
    starting = "starting"
    deleting = "deleting"
    deleted = "deleted"
```

## State Transition Rules

| From State | Operation | To State | Locked During | Duration |
|-----------|-----------|----------|--------------|----------|
| `creating` | (async) | `normal` / `failed` | Yes | ~30s (timeout 60s) |
| `normal` | `shutdown` | `shutting_down` | Yes | ~10s |
| `shutting_down` | (async) | `stopped` | Yes | ~10s |
| `stopped` | `start` | `starting` | Yes | ~10s |
| `starting` | (async) | `normal` | Yes | ~10s |
| `failed` | `start` | `starting` | Yes | ~10s |
| `failed` | `delete` | `deleting` | Yes | ~5s |
| `stopped` | `delete` | `deleting` | Yes | ~5s |
| `deleting` | (async) | `deleted` | Yes | ~5s |
| `deleted` | (none) | — | N/A | Permanent |

**Rules**:
- Transitions not listed above are rejected with `409 Conflict`.
- While in transitional states (`creating`, `shutting_down`, `starting`, `deleting`), all lifecycle operations are rejected.
- `delete` is only allowed from `stopped` or `failed` — attempting from `normal` returns `403 Forbidden`.
- Soft-deleted hosts (`deleted_at IS NOT NULL`) do not appear in list queries but retain DB records.

## Quota Rule

- Max **100 hosts** per user.
- Count = `SELECT COUNT(*) FROM lecs_hosts WHERE user_id = ? AND deleted_at IS NULL`
- Includes all states except `deleted` (i.e., `creating`, `normal`, `failed`, `shutting_down`, `stopped`, `starting`, `deleting`).

## Validation Rules

| Rule | Field | Validation | Error Message |
|------|-------|-----------|---------------|
| VR-001 | hostname | `^[\w]{4,10}$`, no `_` start | "主机名仅支持英文、数字、下划线，长度4-10字符，不可以下划线开头" |
| VR-002 | username | `^[a-zA-Z0-9_@.+-]{4,16}$` | "用户名长度4-16字符" |
| VR-002 | password | `^[a-zA-Z0-9_@#$%^&+=!-]{8,32}$` | "密码长度8-32字符" |
| VR-003 | duration | `int` in {1–9, 12, 24} | "请选择有效的购买时长" |
| VR-007 | spec_id | Must be a valid spec_id from INSTANCE_SPECS | "请选择有效的实例规格" |
| VR-004 | billing_mode | `"subscription"` or `"on_demand"` | "请选择有效的计费模式" |
| VR-009 | ip_address | Valid IPv4 format (when ip_mode=manual) | "请输入有效的IP地址" |
| VR-009 | ip_mask | int 8–24 (when ip_mode=manual) | "请选择有效的掩码值" |
| VR-005 | hostname uniqueness | Unique per user | "主机名已存在" |

## Relationships

- **LECSHost** → **User**: Many-to-One via `user_id` FK. User `ON DELETE CASCADE` is **not** implemented — hosts must be explicitly deleted before user deletion.

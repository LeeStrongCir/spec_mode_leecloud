# Data Model: LECS Host Management

## Entities

### LECSHost (lecs_hosts)

Represents a cloud server instance created by a user.

| Field | Type | Constraint | Description |
|-------|------|------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique host identifier |
| `user_id` | UUID | FOREIGN KEY (users.id), INDEX | Owner user |
| `name` | String(64) | Nullable | Display name |
| `status` | LechsHostStatus | NOT NULL | Current state: `creating`, `running`, `stopped`, `error`, `deleted` |
| `region` | String(50) | NOT NULL, INDEX | Deployment region (e.g., "华北-北京四") |
| `billing_mode` | LechsBillingMode | NOT NULL | `monthly` (包年/包月) or `hourly` (按需计费) |
| `duration` | Integer | Nullable | Months for prepaid billing |
| `expire_at` | DateTime | Nullable | Billing expiry timestamp |
| `instance_type_id` | String(50) | NOT NULL | FK to InstanceType.name |
| `os_image_id` | String(50) | NOT NULL | FK to OSImage.name |
| `enable_public_ip` | Boolean | DEFAULT true | Whether a public IP is assigned |
| `bandwidth_billing_mode` | String(20) | Nullable | `bandwidth` (按带宽) or `traffic` (按流量) |
| `bandwidth_mbps` | Integer | CHECK 1-2000 | Public bandwidth size |
| `public_ip` | String(45) | Nullable | Assigned public IP address |
| `private_ip` | String(45) | NOT NULL | VPC private IP address |
| `enable_security` | Boolean | DEFAULT true | Host security protection |
| `auto_renew` | Boolean | DEFAULT false | Auto-renewal flag |
| `quantity` | Integer | DEFAULT 1 | Number of identical hosts |
| `price_amount` | Numeric(10,2) | Nullable | Total purchase price at creation |
| `created_at` | DateTime | NOT NULL | Creation timestamp (UTC) |
| `updated_at` | DateTime | NOT NULL | Last update timestamp (UTC) |
| `deleted_at` | DateTime | Nullable | Soft-delete timestamp |

**Status Transitions**:
```
creating → running  (via background provisioning)
running → stopped   (user action: future scope)
stopped → running   (user action: future scope)
any → error         (provisioning failure)
any → deleted       (soft delete; Recycle Bin)
```

### InstanceType (instance_types)

Catalog of compute families (seeded at startup).

| Field | Type | Constraint | Description |
|-------|------|------------|-------------|
| `name` | String(50) | PRIMARY KEY | e.g., "x1", "s3", "c7" |
| `category` | String(20) | NOT NULL | `economy`, `high_cost_performance`, `high_performance` |
| `description` | Text | Nullable | Category description |

### InstanceSpec (instance_specs)

Concrete compute configurations under an instance type (seeded at startup).

| Field | Type | Constraint | Description |
|-------|------|------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique spec ID |
| `instance_type_id` | String(50) | FOREIGN KEY (instance_types.name), NOT NULL | Parent instance type |
| `vcpus` | Integer | NOT NULL | Number of virtual CPUs |
| `memory_gib` | Integer | NOT NULL | Memory in GiB |
| `system_disk_type` | String(20) | NOT NULL | e.g., "通用型SSD", "高性能SSD" |
| `system_disk_gib` | Integer | NOT NULL | System disk capacity |
| `monthly_price` | Numeric(10,2) | NOT NULL | Monthly price in CNY |
| `is_available` | Boolean | DEFAULT true | Whether currently purchasable |

### OSImage (os_images)

Operating system templates (seeded at startup).

| Field | Type | Constraint | Description |
|-------|------|------------|-------------|
| `name` | String(100) | PRIMARY KEY | e.g., "Huawei Cloud EulerOS" |
| `family` | String(50) | NOT NULL | OS family: `Linux`, `Windows` |
| `version` | String(50) | NOT NULL | e.g., "2.0 标准版 64位" |
| `arch` | String(10) | NOT NULL | Architecture: `x86_64`, `arm64` |
| `default_disk_gib` | Integer | NOT NULL | Minimum system disk |
| `is_available` | Boolean | DEFAULT true | Currently offered |
| `sort_order` | Integer | NOT NULL | Display order (Huawei EulerOS first) |

## Relationships

- **User** → **LECSHost**: 1:N (one user owns many hosts)
- **LECSHost** → **InstanceType**: N:1 (many hosts share one instance type definition)
- **LECSHost** → **InstanceSpec**: N:1 (many hosts share one spec configuration)
- **LECSHost** → **OSImage**: N:1 (many hosts share one OS template)
- **InstanceType** → **InstanceSpec**: 1:N (one type has multiple concrete specs)

## Indexes

| Index | Fields | Purpose |
|-------|--------|---------|
| `ix_lecs_hosts_user_id` | `user_id` | Filter hosts by owner |
| `ix_lecs_hosts_region` | `region` | Filter by region |
| `ix_lecs_hosts_status` | `status` | Filter by lifecycle status |
| `ix_lecs_hosts_deleted_at` | `deleted_at` | Recycle Bin queries (IS NOT NULL) |

## Validation Rules

1. **Quota check**: User's active host count + new quantity ≤ 200
2. **Single request limit**: quantity ≤ 100
3. **Bandwidth range**: 1-2000 Mbps (only if enable_public_ip is true)
4. **Duration required**: If billing_mode == "monthly", duration must be 1-36 months
5. **Instance spec valid**: instance_type_id + instance_spec_id must reference existing records
6. **OS image valid**: os_image_id must reference an available OSImage
7. **Name uniqueness per user**: No two active hosts for the same user can have the same name
8. **Cannot delete running host**: Status must be `stopped` or `creating` before soft-deletion (future scope: stop first)

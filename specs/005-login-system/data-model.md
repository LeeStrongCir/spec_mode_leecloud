# Data Model: 用户登录系统

**Feature**: 005-login-system  
**Date**: 2026-05-06

---

## User

系统使用者，登录认证的核心实体。

| Field | Type | Constraint | Description |
|-------|------|------------|-------------|
| `id` | UUID | PK, NOT NULL | 唯一用户标识，系统生成 |
| `username` | VARCHAR(50) | UNIQUE, NOT NULL | 用户名，登录凭证之一 |
| `email` | VARCHAR(254) | UNIQUE, NOT NULL | 邮箱地址，登录凭证之一，RFC 5321 格式验证 |
| `password_hash` | VARCHAR(255) | NOT NULL | Argon2id 哈希密码，永不存储明文 |
| `status` | ENUM | NOT NULL, DEFAULT 'active' | 用户状态: `active` / `locked` / `disabled` |
| `failed_login_count` | SMALLINT | NOT NULL, DEFAULT 0 | 连续登录失败次数，成功登录后重置为 0 |
| `last_login_at` | TIMESTAMP WITH TIME ZONE | NULLABLE | 上次成功登录时间 |
| `last_login_ip` | VARCHAR(45) | NULLABLE, ENCRYPTED | 上次登录来源 IP（加密存储） |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | 账号创建时间 |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | 最后更新时间 |

**Validation Rules** (from spec requirements):
- FR-002: username 或 email 均可作为登录标识
- FR-011: failed_login_count 达到阈值时，status 自动转为 `locked`
- FR-018: last_login_ip 必须加密存储

**State Transitions**:
```
active ──(连续登录失败≥阈值)──→ locked
locked ──(锁定时间到期/管理员解锁)──→ active
active ──(管理员操作)──→ disabled
disabled ──(管理员操作)──→ active
```

---

## LoginRecord

一次登录尝试的完整记录。所有登录（成功+失败）都必须产生记录 (FR-006)。

| Field | Type | Constraint | Description |
|-------|------|------------|-------------|
| `id` | UUID | PK, NOT NULL | 日志记录唯一标识 |
| `user_id` | UUID | FK → User.id, NULLABLE | 关联用户（失败登录可能为空） |
| `login_time` | TIMESTAMP WITH TIME ZONE | NOT NULL | 登录尝试时间戳 |
| `ip_address` | VARCHAR(45) | NOT NULL, ENCRYPTED | 来源 IPv4/IPv6 地址（加密存储） |
| `device_type` | VARCHAR(50) | NOT NULL | 设备类型解析: `desktop` / `mobile` / `tablet` / `unknown` |
| `browser` | VARCHAR(100) | NOT NULL | 浏览器 UA 解析结果 (Chrome 120, Safari 17 等) |
| `operating_system` | VARCHAR(100) | NOT NULL | 操作系统 (Windows 11, macOS 14, Ubuntu 22.04 等) |
| `status` | ENUM | NOT NULL | 登录结果: `success` / `failed` |
| `failure_reason` | VARCHAR(255) | NULLABLE | 失败原因: `wrong_password` / `user_not_found` / `account_locked` / `account_disabled` |
| `is_anomalous` | BOOLEAN | NOT NULL, DEFAULT false | 是否异常登录（异地、非常用设备等） |
| `ip_geo_location` | VARCHAR(255) | NULLABLE | IP 归属地信息（城市/国家） |

**Validation Rules** (from spec requirements):
- FR-006: 每次登录尝试（无论成功或失败）都产生记录
- FR-007: 必须包含所有列出的字段
- FR-008: 失败登录必须有 failure_reason
- FR-009: is_anomalous 标记异地登录行为
- FR-013: 列表按 login_time 倒序排列，支持分页
- FR-018: ip_address 等敏感数据加密存储

---

## Session

用户登录成功后建立的身份凭证记录。

| Field | Type | Constraint | Description |
|-------|------|------------|-------------|
| `id` | UUID | PK, NOT NULL | 会话唯一标识 |
| `user_id` | UUID | FK → User.id, NOT NULL | 关联用户 |
| `access_token_jti` | VARCHAR(36) | NOT NULL, UNIQUE | Access Token 的 JWT ID (用于撤销) |
| `refresh_token_hash` | VARCHAR(255) | NOT NULL, UNIQUE | Refresh Token 的 SHA-256 哈希 |
| `access_token_expires_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | Access Token 过期时间 (15min) |
| `refresh_token_expires_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | Refresh Token 过期时间 (7d) |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | 会话创建时间 |
| `last_used_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | 最后使用时间 |
| `revoked` | BOOLEAN | NOT NULL, DEFAULT false | 是否已撤销（登出时设为 true） |
| `revoked_at` | TIMESTAMP WITH TIME ZONE | NULLABLE | 撤销时间 |

**Validation Rules** (from spec requirements):
- FR-003: 凭证验证通过后创建 Session
- FR-005: 登出时设置 revoked = true
- FR-016: "记住我"功能通过延长 refresh_token_expires_at 实现（30 天）

**Relationships**:
- Session.user_id → User.id (Many-to-One)
- 一个 User 可以有多个 Session（多设备并发登录）

---

## AccountLock

因连续登录失败而触发的临时安全限制记录。

| Field | Type | Constraint | Description |
|-------|------|------------|-------------|
| `id` | UUID | PK, NOT NULL | 锁定记录唯一标识 |
| `user_id` | UUID | FK → User.id, NOT NULL | 被锁定用户 |
| `locked_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | 锁定开始时间 |
| `unlock_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | 预计自动解锁时间 |
| `failed_attempts` | SMALLINT | NOT NULL | 触发锁定的连续失败次数 |
| `lock_reason` | VARCHAR(255) | NOT NULL | 锁定原因描述 |
| `released_at` | TIMESTAMP WITH TIME ZONE | NULLABLE | 实际解锁时间（自动或手动） |
| `released_by` | UUID | FK → User.id, NULLABLE | 解锁操作人（NULL=自动解锁） |

**Validation Rules** (from spec requirements):
- FR-011: 连续失败计数达到阈值时创建锁定记录
- unlock_at 默认 = locked_at + 15 分钟
- 手动解锁时 released_by 填充为管理员用户 ID

**Relationships**:
- AccountLock.user_id → User.id (Many-to-One)
- AccountLock.released_by → User.id (Many-to-One, 可选)

---

## Entity Relationship Diagram

```
User (1) ─────── (N) LoginRecord
  │                     │
  │                     └── [user_id nullable for failed logins]
  │
  ├─── (N) Session
  │         └── [one user, multiple concurrent sessions]
  │
  └─── (N) AccountLock
            └── [tracks lock/unlock history]
```

---

## Indexing Strategy

| Table | Index | Purpose |
|-------|-------|---------|
| User | UNIQUE(username), UNIQUE(email) | 登录凭证查找 |
| LoginRecord | INDEX(user_id, login_time DESC) | 用户登录历史查询 (FR-012) |
| LoginRecord | INDEX(ip_address, login_time DESC) | IP 维度审计 (FR-015) |
| LoginRecord | INDEX(status, login_time DESC) | 成功/失败筛选 (FR-015) |
| Session | UNIQUE(access_token_jti) | 令牌撤销查找 |
| Session | UNIQUE(refresh_token_hash) | Refresh Token 验证 |
| Session | INDEX(user_id, revoked) | 活跃会话查询 |
| AccountLock | INDEX(user_id, released_at) | 用户锁定状态查询 |

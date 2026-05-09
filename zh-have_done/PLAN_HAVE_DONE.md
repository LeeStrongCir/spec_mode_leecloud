# /speckit.plan 完整演示示例

> 本文件记录 `/speckit.plan` 命令对 `005-login-system` 功能的完整执行流程和产出。

---

## 触发命令

```
/speckit.plan
```

**前置条件**: `specs/005-login-system/spec.md` 已存在（由 `/speckit.specify` 生成）。

---

## Step 1: Setup — 运行配置脚本

```bash
bash .specify/scripts/bash/setup-plan.sh --json
```

**输出**:

```json
{
  "FEATURE_SPEC": "/mnt/d/project_workspace/spec_mode_leecloud/specs/005-login-system/spec.md",
  "IMPL_PLAN": "/mnt/d/project_workspace/spec_mode_leecloud/specs/005-login-system/plan.md",
  "SPECS_DIR": "/mnt/d/project_workspace/spec_mode_leecloud/specs/005-login-system",
  "BRANCH": "main",
  "HAS_GIT": "true"
}
```

脚本同时将 `plan-template.md` 拷贝为 `specs/005-login-system/plan.md`。

---

## Step 2: Pre-Execution — Hook 检查

读取 `.specify/extensions.yml` 中的 `hooks.before_plan`：

```yaml
before_plan:
  - extension: git
    command: speckit.git.commit
    enabled: true
    optional: true
    prompt: Commit outstanding changes before planning?
    description: Auto-commit before implementation planning
```

这是 **optional** 钩子，系统输出：

> ## Extension Hooks
>
> **Optional Pre-Hook**: git
> Command: `/speckit.git.commit`
> Description: Auto-commit before implementation planning
> Prompt: Commit outstanding changes before planning?
> To execute: `/speckit.git.commit`

---

## Step 3: Load Context

### 3a. 读取 Feature Spec (`spec.md`)

提取关键信息：
- 4 个 User Story（P1 登录 → P2 记录信息 → P3 历史查看 → P3 管理员审计）
- 18 条 Functional Requirements (FR-001 至 FR-018)
- 4 个 Key Entities: User, LoginRecord, Session/Token, AccountLock
- 7 条 Measurable Success Criteria
- 8 条 Assumptions
- 标注为 HIGH 风险（认证模块变更）

### 3b. 读取 Constitution (`constitution.md`)

提取关键约束：

| 宪章原则 | 具体要求 |
|----------|----------|
| TDD 非协商 | 所有生产级功能代码在实现前由失败的测试定义 |
| 测试金字塔 | Unit 70% / Integration 20% / E2E 10%（高风险项目 50/30/20） |
| 覆盖率目标 | 核心业务逻辑 100%，核心服务 90%+，UI 组件 60-70% |
| 安全测试 | Pre-commit Secret Scan → CI SAST+SCA → Staging DAST，零 Critical/High |
| 性能 | p95 偏离基线 ≤ 5% |
| 无障碍 | WCAG 2.2 Level AA，axe-core CI 扫描 0 Critical Violation |
| CI/CD Gate | PR Gate < 5min, Merge Gate < 30min, Post-deploy < 2min |
| 测试数据 | 自包含、Ephemeral DB、禁止生产数据、GDPR 合规 |

### 3c. 加载 Plan Template

`plan-template.md` 定义以下必填章节：
- Summary
- Technical Context (所有字段标记 NEEDS CLARIFICATION)
- Constitution Check
- Project Structure (Documentation 目录 + Source Code 目录)
- Complexity Tracking

---

## Step 4: Phase 0 — Outline & Research

### 4a. 提取 NEEDS CLARIFICATION 项

plan-template 的 Technical Context 中所有初始值均为 NEEDS CLARIFICATION：

| 字段 | 未决内容 |
|------|----------|
| Language/Version | [NEEDS CLARIFICATION] |
| Primary Dependencies | [NEEDS CLARIFICATION] |
| Storage | [NEEDS CLARIFICATION] |
| Testing | [NEEDS CLARIFICATION] |
| Target Platform | [NEEDS CLARIFICATION] |
| Project Type | [NEEDS CLARIFICATION] |
| Performance Goals | [NEEDS CLARIFICATION] |
| Constraints | [NEEDS CLARIFICATION] |
| Scale/Scope | [NEEDS CLARIFICATION] |

### 4b. 派发研究 Agent (Parallel)

```typescript
// Librarian agent: Backend auth stack research for FastAPI
task(subagent_type="librarian", run_in_background=true, load_skills=[], description="Research backend auth stack", ...);
```

### 4c. 研究结果 → research.md

```markdown
# Research: 用户登录系统技术决策

**Feature**: 005-login-system
**Date**: 2026-05-06

## Decision 1: 后端框架 — Python 3.11 + FastAPI 0.115+

**Rationale**:
- FastAPI 原生异步支持（async/await），自动 OpenAPI 文档生成
- Pydantic v2 内置数据验证，与 SQLAlchemy 2.0 兼容良好
- 宪章要求的安全扫描工具（bandit SAST、CodeQL、Semgrep）全面支持 Python
- 社区活跃，企业采用率高，适合安全敏感型应用

**Alternatives considered**:
- Node.js + Express/TypeScript: 生态成熟但异步模型与 Python 团队技能不匹配
- Go + Gin: 性能好但学习曲线陡，认证生态不如 Python 丰富

## Decision 2: 认证模式 — JWT (httpOnly Cookie) + Refresh Token Rotation

**Rationale**:
- Access Token 存储在 httpOnly Secure SameSite=Lax Cookie 中，防 XSS（宪章安全要求）
- JWT 无状态设计降低服务端存储压力，水平扩展友好
- Refresh Token 在服务端存储哈希并每次轮换，支持令牌撤销
- Access Token TTL 设为 15 分钟，Refresh Token TTL 设为 7 天
- JWT 包含 `typ` 声明（"access"/"refresh"）防止令牌混淆使用
- JWT 包含 `jti` (JWT ID) UUID 用于单个令牌撤销

**Alternatives considered**:
- 纯 Session（服务端存储）: 简单但不水平扩展，需 Redis/集群共享
- localStorage 存储 JWT: OWASP 明确反对，XSS 可窃取令牌

## Decision 3: 密码哈希 — argon2-cffi (Argon2id)

**Rationale**:
- Argon2id 赢得 2015 Password Hashing Competition，RFC 9106 标准化
- OWASP #1 推荐算法，memory-hard 抗 GPU/ASIC 攻击
- bcrypt 在 GPU 下 crack 速度 95,000 H/s，Argon2id 仅 380 H/s（差 250 倍）

**Alternatives considered**:
- bcrypt: 可接受但安全性弱于 Argon2id
- passlib: ⚠️ 已废弃（2020年最后更新）
- hashlib.scrypt: 标准库但参数调优需手动

## Decision 4: 数据库 — SQLite (dev) → PostgreSQL (prod)

**Rationale**:
- SQLite 零配置，单文件，适合开发、测试、CI
- PostgreSQL 提供完整 ACID、连接池、并发控制
- SQLAlchemy 2.0 async + Alembic 同时兼容两者

## Decision 5: ORM 与迁移 — SQLAlchemy 2.0 + Alembic 1.14+

## Decision 6: 测试框架 — pytest + pytest-asyncio + Playwright

## Decision 7: 速率限制 — slowapi

## Decision 8: 前端渲染 — Jinja2 SSR + HTMX

## Decision 9: 安全扫描工具链

| 环节 | 工具 |
|------|------|
| Pre-commit | detect-secrets (密钥扫描) |
| CI SAST | bandit (Python 安全扫描) |
| CI SCA | pip-audit (依赖漏洞) |
| Staging DAST | OWASP ZAP |
| Linting | ruff |
```

---

## Step 5: Fill Technical Context (Resolved)

根据 research.md 的研究结论，将 plan.md 中的 Technical Context 从 NEEDS CLARIFICATION 替换为具体值：

```markdown
## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI 0.115+, SQLAlchemy 2.0 (async), PyJWT 2.9+,
  argon2-cffi 23.1+, pydantic-settings 2.5+, slowapi, fastapi-csrf-protect
**Storage**: SQLite (aiosqlite) 开发/测试 → PostgreSQL (asyncpg) 生产,
  Alembic 1.14+ 管理迁移
**Testing**: pytest + pytest-asyncio (异步) + pytest-cov + Playwright (E2E)
**Target Platform**: Linux server (x86_64 / aarch64)
**Project Type**: web-service (前后端分离全栈应用)
**Performance Goals**: 500 并发登录/分钟，验证响应 p95 ≤ 3s，登录记录写入 p95 ≤ 100ms
**Constraints**: JWT httpOnly Cookie 存储，CSRF 防护，Argon2id 密码哈希，
  PII 数据加密，CI/CD 多层 Hard Gate，认证模块 HIGH 风险
**Scale/Scope**: 首期单实例部署，10K+ 注册用户，支持水平扩展
```

---

## Step 6: Constitution Check

根据 constitution.md 中的约束，逐项评估：

```markdown
## Constitution Check

| Gate | Constitution Requirement | Status | Notes |
|------|------------------------|--------|-------|
| TDD 非协商 | FR-001~FR-005 核心认证逻辑 MUST 由失败的测试先行定义 | ✅ PASS | 所有 AuthService 方法在实现前编写测试 |
| 测试覆盖率 | 核心业务逻辑 100%，核心服务 90%+，UI 60-70% | ✅ PASS | pytest-cov 配置，CI Gate 阻塞 |
| 高风险回归 | 认证模块变更 = HIGH 风险，需完整子系统回归 + 关键路径 E2E | ✅ PASS | 每个 PR 执行 |
| 安全测试 | Pre-commit Secret Scan → SAST+SCA → DAST，零 Critical/High | ✅ PASS | bandit + pip-audit + OWASP ZAP |
| 测试代码即生产代码 | 相同编码规范、Linting、Code Review 标准 | ✅ PASS | ruff 覆盖 src/ + tests/ |
| 性能 p95 基线 | p95 偏离不超过 5% | ✅ PASS | k6 性能冒烟测试 |
| 无障碍 WCAG 2.2 AA | axe-core CI 扫描 0 Critical Violation | ⚠️ DEFERRED | SSR 原生可访问性好，延至 E2E 阶段 |
| 测试数据管理 | 自包含数据、Ephemeral DB、禁止生产数据 | ✅ PASS | SQLite 内存 DB 隔离 |

> 所有 Hard Gates 通过。1 项软性偏离（无障碍测试延至 E2E）已记录。
```

---

## Step 7: Phase 1 — Design & Contracts

### 7a. 生成 data-model.md

从 spec 的 Key Entities 提取为完整数据模型：

```markdown
# Data Model: 用户登录系统

## User

| Field | Type | Constraint | Description |
|-------|------|------------|-------------|
| id | UUID | PK, NOT NULL | 唯一用户标识 |
| username | VARCHAR(50) | UNIQUE, NOT NULL | 用户名 |
| email | VARCHAR(254) | UNIQUE, NOT NULL | 邮箱地址，RFC 5321 验证 |
| password_hash | VARCHAR(255) | NOT NULL | Argon2id 哈希，永不存明文 |
| status | ENUM | NOT NULL, DEFAULT 'active' | active / locked / disabled |
| failed_login_count | SMALLINT | DEFAULT 0 | 连续失败次数 |
| last_login_at | TIMESTAMP WITH TZ | NULLABLE | 上次成功登录时间 |
| last_login_ip | VARCHAR(45) | NULLABLE, ENCRYPTED | 上次登录 IP (加密) |
| created_at | TIMESTAMP WITH TZ | DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP WITH TZ | DEFAULT NOW() | 更新时间 |

**State Transitions**:
```
active ──(连续失败≥阈值)──→ locked
locked ──(时间到期/管理员解锁)──→ active
active ──(管理员操作)──→ disabled
```

## LoginRecord

| Field | Type | Constraint | Description |
|-------|------|------------|-------------|
| id | UUID | PK, NOT NULL | 记录 ID |
| user_id | UUID | FK → User.id, NULLABLE | 关联用户（失败可为空）|
| login_time | TIMESTAMP WITH TZ | NOT NULL | 登录尝试时间 |
| ip_address | VARCHAR(45) | NOT NULL, ENCRYPTED | IPv4/IPv6 (加密) |
| device_type | VARCHAR(50) | NOT NULL | desktop / mobile / tablet |
| browser | VARCHAR(100) | NOT NULL | Chrome 120, Safari 17 等 |
| operating_system | VARCHAR(100) | NOT NULL | Windows 11, macOS 14 等 |
| status | ENUM | NOT NULL | success / failed |
| failure_reason | VARCHAR(255) | NULLABLE | wrong_password / locked 等 |
| is_anomalous | BOOLEAN | DEFAULT false | 异地/异常登录标记 |
| ip_geo_location | VARCHAR(255) | NULLABLE | IP 归属地 |

## Session

| Field | Type | Constraint | Description |
|-------|------|------------|-------------|
| id | UUID | PK, NOT NULL | 会话 ID |
| user_id | UUID | FK → User.id, NOT NULL | 关联用户 |
| access_token_jti | VARCHAR(36) | UNIQUE, NOT NULL | JWT ID (用于撤销) |
| refresh_token_hash | VARCHAR(255) | UNIQUE, NOT NULL | 刷新令牌 SHA-256 哈希 |
| access_token_expires_at | TIMESTAMP WITH TZ | NOT NULL | 过期时间 (15min) |
| refresh_token_expires_at | TIMESTAMP WITH TZ | NOT NULL | 过期时间 (7d) |
| created_at | TIMESTAMP WITH TZ | DEFAULT NOW() | 创建时间 |
| last_used_at | TIMESTAMP WITH TZ | DEFAULT NOW() | 最后使用时间 |
| revoked | BOOLEAN | DEFAULT false | 是否已撤销 |
| revoked_at | TIMESTAMP WITH TZ | NULLABLE | 撤销时间 |

## AccountLock

| Field | Type | Constraint | Description |
|-------|------|------------|-------------|
| id | UUID | PK, NOT NULL | 锁定记录 ID |
| user_id | UUID | FK → User.id, NOT NULL | 被锁定用户 |
| locked_at | TIMESTAMP WITH TZ | NOT NULL | 锁定开始时间 |
| unlock_at | TIMESTAMP WITH TZ | NOT NULL | 预计自动解锁时间 |
| failed_attempts | SMALLINT | NOT NULL | 触发锁定的失败次数 |
| lock_reason | VARCHAR(255) | NOT NULL | 锁定原因 |
| released_at | TIMESTAMP WITH TZ | NULLABLE | 实际解锁时间 |
| released_by | UUID | FK → User.id, NULLABLE | 解锁操作人 |

## Relationship Diagram

```
User (1) ─────── (N) LoginRecord
  │                     │
  │                     └── [user_id nullable for failed logins]
  ├─── (N) Session
  └─── (N) AccountLock
```

## Indexing Strategy

| Table | Index | Purpose |
|-------|-------|---------|
| User | UNIQUE(username), UNIQUE(email) | 登录凭证查找 |
| LoginRecord | INDEX(user_id, login_time DESC) | 用户登录历史 (FR-012) |
| LoginRecord | INDEX(ip_address, login_time DESC) | IP 维度审计 (FR-015) |
| LoginRecord | INDEX(status, login_time DESC) | 成功/失败筛选 (FR-015) |
| Session | UNIQUE(access_token_jti), UNIQUE(refresh_token_hash) | 令牌撤销查找 |
| Session | INDEX(user_id, revoked) | 活跃会话查询 |
| AccountLock | INDEX(user_id, released_at) | 用户锁定状态查询 |
```

### 7b. 生成 contracts/auth-api.md

```markdown
# Authentication API Contracts

## POST /api/auth/login

**Request Body**:
```json
{
  "identifier": "string",     // 用户名或邮箱
  "password": "string",
  "remember_me": false
}
```

**Response 200 OK** (成功):
```json
{
  "status": "success",
  "message": "登录成功",
  "user": { "id": "...", "username": "zhangsan", "email": "zhangsan@example.com" }
}
```
- Set-Cookie: `access_token=<JWT>; HttpOnly; Secure; SameSite=Lax; Max-Age=900`
- Set-Cookie: `refresh_token=<JWT>; HttpOnly; Secure; SameSite=Lax; Max-Age=604800`

**Response 401** (凭证错误):
```json
{ "status": "error", "error_code": "INVALID_CREDENTIALS", "message": "用户名或密码错误" }
```

**Response 423** (账号锁定):
```json
{
  "status": "error", "error_code": "ACCOUNT_LOCKED",
  "message": "账号已锁定，15 分钟后重试",
  "unlock_at": "2026-05-06T10:45:00Z"
}
```

**Response 429** (速率限制):
```json
{ "status": "error", "error_code": "RATE_LIMITED", "message": "请 60s 后重试", "retry_after": 60 }
```

## POST /api/auth/logout
**Headers**: Cookie: `access_token=<jwt>`
**Response 200**: `{ "status": "success", "message": "已登出" }`
- 设置 Session.revoked = true, 清除 Cookie

## POST /api/auth/refresh
**Headers**: Cookie: `refresh_token=<jwt>`
**Response 200**: 新 Cookie，旧令牌轮换

## GET /api/auth/me
**Headers**: Cookie: `access_token=<jwt>`
**Response 200**: 返回当前用户信息
```

### 7c. 生成 contracts/login-record-api.md

```markdown
# Login Record Query API Contracts

## GET /api/auth/login-history
**Headers**: Cookie: `access_token=<jwt>`
**Query Params**: page, page_size, status
**Response 200**: 分页登录记录列表，IP 脱敏展示（用户视角）

## GET /api/admin/login-records
**Headers**: Cookie: `access_token=<jwt>` (需管理员权限)
**Query Params**: page, page_size, user_id, username, start_time, end_time,
  status, ip_address, is_anomalous
**Response 200**: 分页登录记录列表，IP 不脱敏（管理员视角）
**Response 403**: 非管理员用户
```

### 7d. 生成 quickstart.md

```markdown
# Quickstart: 本地开发环境搭建

## 前置条件: Python 3.11+, Git, SQLite

## 步骤:

1. cd backend
2. python3.11 -m venv .venv && source .venv/bin/activate
3. pip install -e ".[dev]"
4. cp .env.example .env  (配置 SECRET_KEY, JWT_SECRET_KEY, DATABASE_URL)
5. alembic upgrade head   (创建所有表)
6. uvicorn src.app.main:app --reload --port 8000
7. pytest --cov=src/app --cov-report=html  (运行测试)
8. ruff check src/ tests/ && bandit -r src/app/
```

### 7e. 更新 AGENTS.md

```markdown
<!-- SPECKIT START -->
Implementation plan: [specs/005-login-system/plan.md](specs/005-login-system/plan.md)
<!-- SPECKIT END -->
```

---

## Step 8: Post-Design Constitution Re-Check

| 宪章要求 | 设计是否符合 |
|----------|-------------|
| TDD + pytest | ✅ pytest 全面支持 TDD 红-绿-重构循环 |
| 核心逻辑 100% 覆盖 | ✅ AuthService 独立编写测试，无外部依赖 |
| 安全: SAST/DAST | ✅ bandit (Python SAST) + pip-audit (SCA) 已配置 |
| 性能: p95 SLO | ✅ FastAPI 异步，500 并发可达 |
| 无障碍: WCAG 2.2 AA | ⚠️ SSR + Jinja2 原生可访问性好，axe-core E2E 阶段引入 |
| CI/CD Pipeline | ✅ pytest + Playwright E2E 可集成 GitHub Actions |

> 宪章检查通过，无阻塞项。

---

## Step 9: Report Completion

```
## ✅ /speckit.plan 完成

Branch: main
Implementation Plan: specs/005-login-system/plan.md

### Phase 0 产出
- ✅ research.md — 9 项技术决策，所有 NEEDS CLARIFICATION 已解决

### Phase 1 产出
- ✅ plan.md — 完整实施规划（技术上下文、宪章检查、项目结构）
- ✅ data-model.md — 4 个实体 + 关系图 + 7 个索引策略
- ✅ contracts/auth-api.md — 4 个认证端点契约
- ✅ contracts/login-record-api.md — 2 个记录查询端点契约
- ✅ quickstart.md — 本地开发环境搭建指南
- ✅ AGENTS.md — 已更新 plan 引用

### Constitution Check 状态
✅ 全部通过（1 项观察项：可访问性延时 E2E）

### 下一步
- /speckit.tasks — 生成依赖排序的实施任务列表
```

---

## Step 10: after_plan Hook 检查

```yaml
after_plan:
  - extension: git
    command: speckit.git.commit
    enabled: true
    optional: true
```

> ## Extension Hooks
>
> **Optional Hook**: git
> Command: `/speckit.git.commit`
> Description: Auto-commit after implementation planning
> Prompt: Commit plan changes?
> To execute: `/speckit.git.commit`

---

## 最终产出文件清单

```
specs/005-login-system/
├── spec.md                           # Feature specification (from /speckit.specify)
├── plan.md                           # Implementation plan (Phase 0+1 输出)
├── research.md                       # Phase 0: 9 项技术决策
├── data-model.md                     # Phase 1: 4 个实体数据模型
├── quickstart.md                     # Phase 1: 开发环境搭建指南
├── contracts/
│   ├── auth-api.md                   # Phase 1: 认证 API 契约 (4 endpoints)
│   └── login-record-api.md           # Phase 1: 登录记录查询契约 (2 endpoints)
└── checklists/
    └── requirements.md               # Updated 包含 post-plan validation
```

---

## 关键决策总结

| 决策 | 选择 | 依据 |
|------|------|------|
| 后端框架 | Python 3.11 + FastAPI | 异步优先，宪章安全工具支持 |
| 认证模式 | JWT httpOnly Cookie + Refresh Token Rotation | OWASP 推荐，XSS 防护 + 令牌撤销 |
| 密码哈希 | argon2-cffi (Argon2id) | OWASP #1，memory-hard，GPU抗性 |
| 数据库 | SQLite (dev) → PostgreSQL (prod) | SQLAlchemy 2.0 async 统一 |
| ORM | SQLAlchemy 2.0 + Alembic | 官方异步支持，迁移管理 |
| 测试 | pytest + Playwright | TDD 标准 + E2E 宪章推荐 |
| 前端 | Jinja2 SSR + HTMX | 低复杂，WCAG 原生可访问 |
# Implementation Plan: 用户登录与登录信息记录

**Branch**: `main` | **Date**: 2026-05-06 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/005-login-system/spec.md`

## Summary

实现一个完整的用户登录系统，包括：凭证认证（邮箱+密码）、JWT/httpOnly Cookie 会话管理、登录信息自动记录、用户查看自己的登录历史、管理员审计全体登录记录。技术栈采用 Python 3.11 + FastAPI 异步框架，SQLAlchemy 2.0 ORM，Argon2id 密码哈希，SQLite (dev) → PostgreSQL (prod) 数据库方案。所有核心认证逻辑遵循宪章 TDD 要求，100% 核心业务逻辑覆盖率。

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI 0.115+, SQLAlchemy 2.0 (async), PyJWT 2.9+, argon2-cffi 23.1+, pydantic-settings 2.5+, slowapi（速率限制）, fastapi-csrf-protect（CSRF 防护）  
**Storage**: SQLite (aiosqlite 驱动) 用于开发和测试 → PostgreSQL (asyncpg 驱动) 用于生产环境，Alembic 1.14+ 管理数据库迁移  
**Testing**: pytest (异步用 pytest-asyncio) + pytest-cov (覆盖率) + Playwright (E2E)  
**Target Platform**: Linux server (x86_64 / aarch64)  
**Project Type**: web-service (前后端分离全栈应用，首期 SSR + HTMX 登录页，后续可扩展 SPA)  
**Performance Goals**: 500 并发登录/分钟，认证验证响应 p95 ≤ 3s，登录记录写入延迟 p95 ≤ 100ms  
**Constraints**: JWT httpOnly Cookie 存储，CSRF 防护，Argon2id 密码哈希满足 OWASP 标准，PII 数据加密存储，CI/CD 多层 Hard Gate，认证模块属 HIGH 风险  
**Scale/Scope**: 首期单实例部署，目标 10K+ 注册用户，支持水平扩展

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Gate | Constitution Requirement | Status | Notes |
|------|------------------------|--------|-------|
| TDD 非协商 | FR-001~FR-005 核心认证逻辑 MUST 由失败的测试先行定义 | ✅ PASS | 所有 AuthService 方法在实现前编写对应测试 |
| 测试覆盖率 | 核心业务逻辑 100%，核心服务 90%+，UI 60-70% | ✅ PASS | pytest-cov 配置，CI Gate 阻塞不达标合入 |
| 高风险回归 | 认证模块变更 = HIGH 风险，需完整子系统回归 + 关键路径 E2E | ✅ PASS | 每个 PR 执行 |
| 安全测试 | Pre-commit Secret Scan → CI SAST+SCA → Staging DAST，零 Critical/High | ✅ PASS | bandit (SAST) + pip-audit (SCA) + OWASP ZAP (DAST) |
| 测试代码即生产代码 | 相同编码规范、Linting、Code Review 标准 | ✅ PASS | ruff linting 同时覆盖 src/ 和 tests/ |
| 性能 p95 基线 | p95 偏离不超过 5% | ✅ PASS | k6 性能冒烟测试随每次提交 |
| 无障碍 WCAG 2.2 AA | axe-core CI 扫描 0 Critical Violation | ⚠️ DEFERRED | SSR 原生可访问性好，axe-core 在 E2E 阶段引入 |
| 测试数据管理 | 自包含数据、Ephemeral DB、禁止生产数据 | ✅ PASS | pytest fixture 创建测试数据，SQLite 内存 DB 隔离 |

> 所有 Hard Gates 通过。1 项软性偏离（无障碍测试延至 E2E 阶段）已记录。

## Project Structure

### Documentation (this feature)

```text
specs/005-login-system/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0: Technical decisions
├── data-model.md        # Phase 1: Data model
├── quickstart.md        # Phase 1: Dev environment setup
├── contracts/           # Phase 1: API contracts
│   ├── auth-api.md      # Authentication endpoints
│   └── login-record-api.md  # Login record query endpoints
└── tasks.md             # Phase 2: Task breakdown (by /speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── pyproject.toml               # Project metadata & dependencies
├── alembic.ini                  # Alembic configuration
├── alembic/
│   ├── env.py
│   └── versions/                # Database migrations
├── src/
│   └── app/
│       ├── __init__.py
│       ├── main.py              # FastAPI application entry point
│       ├── config.py            # Pydantic Settings (env vars)
│       ├── models/              # SQLAlchemy ORM models
│       │   ├── __init__.py
│       │   ├── user.py          # User model
│       │   ├── login_record.py  # LoginRecord model
│       │   └── session.py       # Session/AccountLock models
│       ├── schemas/             # Pydantic request/response schemas
│       │   ├── __init__.py
│       │   ├── auth.py          # Login/Auth schemas
│       │   └── login_record.py  # Login record schemas
│       ├── services/            # Business logic (core, TDD coverage 100%)
│       │   ├── __init__.py
│       │   ├── auth_service.py         # Authentication logic
│       │   ├── password_service.py     # Argon2id hashing
│       │   ├── login_record_service.py # Login recording
│       │   └── rate_limit_service.py   # Brute force protection
│       ├── api/                 # Route handlers
│       │   ├── __init__.py
│       │   ├── auth.py          # /login, /logout, /refresh
│       │   ├── login_record.py  # /login-history, /admin/login-records
│       │   └── deps.py          # FastAPI dependencies (get_db, get_current_user)
│       ├── security/            # Security utilities
│       │   ├── __init__.py
│       │   ├── jwt.py           # Token creation/validation
│       │   └── csrf.py          # CSRF protection
│       └── middleware/          # ASGI middleware
│           ├── __init__.py
│           └── login_logger.py  # Auto-login recording middleware
├── tests/
│   ├── conftest.py              # Shared fixtures (ephemeral DB, factories)
│   ├── unit/
│   │   ├── test_auth_service.py
│   │   ├── test_password_service.py
│   │   └── test_jwt.py
│   ├── integration/
│       ├── test_login_flow.py
│       ├── test_login_record_creation.py
│       └── test_rate_limiting.py
│   └── e2e/
│       ├── test_full_login.py   # Playwright: full browser login flow
│       └── test_admin_dashboard.py
└── frontend/
    ├── templates/               # Jinja2 SSR templates
    │   ├── base.html
    │   ├── login.html
    │   ├── login_history.html
    │   └── admin/
    │       └── login_records.html
    └── static/
        ├── css/
        └── js/
```

**Structure Decision**: Monorepo layout with `backend/` and `frontend/` directories. The backend is a FastAPI web service (JSON API + Jinja2 SSR pages). The frontend uses server-side rendered templates for login flows (lower complexity than SPA, better WCAG accessibility by default). Authentication logic lives in `services/` for testability, with TDD targeting 100% coverage per the constitution.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|--------------------------------------|
| JWT + Refresh Token rotation | OWASP recommends stateless access tokens + stateful refresh for security | Pure session-based auth doesn't scale horizontally; pure JWT can't be revoked |
| CSRF protection layer | httpOnly cookies require CSRF defense | Without it, cross-site request forgery is trivially exploitable |
| Alembic migrations | Production PostgreSQL requires schema versioning | Raw SQL scripts lack rollback support and version tracking |

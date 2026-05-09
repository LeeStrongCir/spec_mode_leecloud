# Research: 用户登录系统技术决策

**Feature**: 005-login-system  
**Date**: 2026-05-06

---

## Decision 1: 后端框架 — Python 3.11 + FastAPI 0.115+

**Rationale**:
- FastAPI 原生异步支持（星号 async/await），自动 OpenAPI 文档生成
- Pydantic v2 内置数据验证，与 SQLAlchemy 2.0 兼容良好
- 宪章要求的安全扫描工具（bandit SAST、CodeQL、Semgrep）全面支持 Python
- 社区活跃，企业采用率高，适合安全敏感型应用

**Alternatives considered**:
- Node.js + Express/TypeScript: 生态成熟但异步模型与 Python 团队技能不匹配
- Go + Gin: 性能好但学习曲线陡，认证生态不如 Python 丰富

---

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

**Security Notes**:
- CSRF 防护通过 double-submit cookie 模式实现（`fastapi-csrf-protect` 库）
- CORS 不启用 `allow_origins=["*"]` with credentials，必须显式白名单
- JWT key 错误统一返回 401，不泄露内部结构（`payload.get()` 而非 `payload[]`）

---

## Decision 3: 密码哈希 — argon2-cffi (Argon2id)

**Rationale**:
- Argon2id 赢得 2015 Password Hashing Competition，RFC 9106 标准化
- OWASP #1 推荐算法，memory-hard 抗 GPU/ASIC 攻击
- bcrypt 在 GPU 下 crack 速度 95,000 H/s，Argon2id 仅 380 H/s（差 250 倍）
- 配置: time_cost=3, memory_cost=65536 (64MB), parallelism=1, hash_len=32, salt_len=16

**Alternatives considered**:
- bcrypt: 可接受但安全性弱于 Argon2id（无 memory-hard 特性）
- passlib: ⚠️ 已废弃（2020年最后更新），有 bcrypt 4.x 兼容性问题
- hashlib.scrypt: Python 标准库但参数调优需手动

---

## Decision 4: 数据库 — SQLite (dev) → PostgreSQL (prod)

**Rationale**:
- SQLite 零配置，单文件，适合开发、测试、CI 环境
- PostgreSQL 提供完整 ACID、连接池、并发控制，适合生产
- SQLAlchemy 2.0 async + Alembic 同时兼容两者，无需代码改动
- 开发用 URL: `sqlite+aiosqlite:///./dev.db`
- 生产用 URL: `postgresql+asyncpg://user:pass@host:5432/dbname`

**Alternatives considered**:
- 纯 SQLite: 高并发写锁瓶颈，不适合生产
- MySQL: 生态成熟但不如 PostgreSQL 功能丰富（JSONB 等）

---

## Decision 5: ORM 与迁移 — SQLAlchemy 2.0 + Alembic

**Rationale**:
- SQLAlchemy 2.0 async 支持，类型声明式 ORM 定义
- Alembic 1.14+ 业界标准迁移工具，支持回滚和版本控制
- Pydantic 2.0 与 SQLAlchemy 2.0 官方兼容

---

## Decision 6: 测试框架 — pytest + pytest-asyncio + Playwright

**Rationale**:
- pytest 是 Python 测试标准，原生支持 TDD Red-Green-Refactor
- pytest-asyncio 支持 FastAPI 异步测试
- pytest-cov 生成覆盖率报告，CI Gate 使用
- Playwright 符合宪章 E2E 推荐工具列表
- 宪章要求覆盖率：核心业务逻辑 100%、核心服务 90%+、UI 60-70%

---

## Decision 7: 速率限制 — slowapi

**Rationale**:
- 轻量级 Redis-backed 速率限制（也用内存兜底）
- 登录接口限制: 5 次/分钟/IP
- 与 FastAPI 集成简单（装饰器模式）

---

## Decision 8: 前端渲染 — Jinja2 SSR + HTMX

**Rationale**:
- 登录页面复杂度低（表单验证 + 跳转），不需要重型 SPA
- SSR 原生可访问性好（WCAG 2.2 AA 更容易达标）
- HTMX 提供 AJAX 交互能力，无需 JavaScript 框架
- 减少前后端交互复杂度，首期足够

**Alternatives considered**:
- React SPA: 适合复杂 UI 但首期过度配置
- Vue + Nuxt: 增加构建链复杂度

---

## Decision 9: 安全扫描工具链

| 环节 | 工具 | 说明 |
|------|------|------|
| Pre-commit | detect-secrets | 密钥扫描，防止敏感信息泄露 |
| CI SAST | bandit | Python 代码安全扫描 |
| CI SCA | pip-audit | 依赖漏洞扫描 |
| Staging DAST | OWASP ZAP | 动态应用安全测试 |
| Linting | ruff | 替代 flake8 + isort + black，速度快 |

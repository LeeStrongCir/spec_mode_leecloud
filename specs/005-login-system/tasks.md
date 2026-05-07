# Tasks: 用户登录与登录信息记录

**Input**: Design documents from `/specs/005-login-system/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: YES — 根据《软件测试宪章》，本功能属 HIGH 风险等级（认证模块变更），必须执行 TDD 开发，核心业务逻辑 100% 覆盖率。

**Organization**: 任务按 User Story 组织，每个 Story 可独立实现和测试。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 可并行执行（不同文件，无依赖）
- **[Story]**: 属于哪个 User Story（US1, US2, US3, US4）
- 描述中包含精确文件路径

## Path Conventions

- **后端**: `backend/src/app/`, `backend/tests/`
- **前端**: `backend/frontend/templates/`, `backend/frontend/static/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: 项目初始化和基础结构搭建

- [x] T001 创建后端项目目录结构 per plan.md（backend/src/app/{models,schemas,services,api,security,middleware}, backend/tests/{unit,integration,e2e}, backend/frontend/{templates,static}, backend/alembic/）

- [x] T002 初始化 `backend/pyproject.toml`，声明生产依赖：fastapi>=0.115, sqlalchemy>=2.0, pydantic>=2.5, pydantic-settings>=2.5, pyjwt>=2.9, argon2-cffi>=23.1, python-multipart, slowapi, fastapi-csrf-protect, aiosqlite, asyncpg, jinja2
- [x] T003 初始化 `backend/pyproject.toml` 开发依赖组：[dev] 包含 pytest, pytest-asyncio, pytest-cov, ruff, bandit, pip-audit, httpx, playwright, k6

- [x] T004 [P] 配置代码质量工具：在 `backend/pyproject.toml` 中配置 ruff（行长度120、Python 3.11 target），创建 `backend/.python-version`（内容：3.11）

- [x] T005 [P] 初始化 Alembic：运行 `alembic init alembic`，配置 `backend/alembic.ini` 和 `backend/alembic/env.py` 支持异步 SQLAlchemy

- [x] T006 创建 `backend/.env.example`，包含：DATABASE_URL=sqlite+aiosqlite:///./dev.db、SECRET_KEY=change-me、JWT_SECRET_KEY=change-me、JWT_ALGORITHM=HS256、JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15、JWT_REFRESH_TOKEN_EXPIRE_DAYS=7、MAX_FAILED_LOGIN_ATTEMPTS=5、LOCKOUT_DURATION_MINUTES=15

- [x] T007 [P] 创建 `backend/src/app/__init__.py` 和 `backend/src/app/config.py`（基于 pydantic-settings 的环境配置加载，含上述所有环境变量，带类型验证和默认值）

- [x] T008 [P] 创建 `backend/src/app/main.py`：FastAPI 应用入口，配置 CORS 中间件（显式 Origin 白名单，禁用 allow_credentials + "*" 组合）、Jinja2 模板引擎、静态文件挂载

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 所有 User Story 的核心基础设施，必须在任何 User Story 之前完成

**⚠️ CRITICAL**: 此阶段未完成，任何 User Story 工作都不能开始

### Tests for Foundational Layer ⚠️

- [x] T009 [P] 编写 Database 连接测试（Ephemeral SQLite 内存库）：`backend/tests/unit/test_database.py` — 验证 async session 创建、事务回滚、连接关闭

- [x] T010 [P] 编写 JWT Token 单元测试：`backend/tests/unit/test_jwt.py` — 验证 access_token 创建/解析、refresh_token 创建/解析、typ 声明区分、过期验证、jti 生成

- [x] T010 [P] 编写 Password Hash 单元测试：`backend/tests/unit/test_password_service.py` — 验证 Argon2id 哈希生成、密码验证、错误密码拒绝、check_needs_rehash

### Implementation

- [x] T010 创建数据库异步引擎和会话工厂：`backend/src/app/db.py`（create_async_engine + async_sessionmaker，支持 SQLite/PostgreSQL URL 切换，连接池配置）

- [x] T010 实现 JWT 工具模块：`backend/src/app/security/jwt.py`（create_access_token、create_refresh_token、decode_token 函数，含 typ/jti/exp/sub 声明，HS256 算法）

- [x] T010 实现密码哈希服务：`backend/src/app/services/password_service.py`（hash_password、verify_password、needs_rehash 函数，使用 argon2-cffi，time_cost=3, memory_cost=65536）

- [x] T010 实现 CSRF 保护配置：`backend/src/app/security/csrf.py`（double-submit cookie 模式，fastapi-csrf-protect 集成）

- [x] T010 创建全局异常处理中间件：`backend/src/app/middleware/error_handler.py`（统一定制 HTTPException 处理，JSON 错误响应格式，不泄露内部堆栈）

**Checkpoint**: 数据库连接、JWT 令牌、密码哈希、CSRF 保护、异常处理全部就绪

---

## Phase 3: User Story 1 - 用户通过凭证登录系统 (Priority: P1) 🎯 MVP

**Goal**: 用户能通过邮箱/用户名+密码登录，验证通过后建立会话并跳转，支持记住我功能

**Independent Test**: 输入正确凭证可成功登录并获得有效会话 Cookie；输入错误凭证被拒绝并得到统一错误提示；整个流程不依赖其他 Story

### Tests for User Story 1 ⚠️

- [x] T010 [P] [US1] 编写 AuthService.authenticate 单元测试：`backend/tests/unit/test_auth_service.py` — 验证成功登录返回 User 对象、错误密码抛出异常、锁定账号拒绝登录、不存在的用户名行为

- [x] T010 [P] [US1] 编写 User 创建 fixture 测试：`backend/tests/conftest.py` — 验证测试工厂能创建有效 User（含 password_hash、status=active）

- [x] T010 [US1] 编写登录端点集成测试：`backend/tests/integration/test_login_flow.py` — 验证 POST /api/auth/login 的成功/失败路径、Cookie 设置、错误响应格式

### Implementation

- [x] T020 [P] [US1] 创建 User SQLAlchemy ORM 模型：`backend/src/app/models/user.py`（id, username, email, password_hash, status, failed_login_count, last_login_at, last_login_ip, created_at, updated_at 字段，含 UNIQUE 约束和 Enum）

- [x] T021 [P] [US1] 创建 Pydantic 登录请求/响应 Schema：`backend/src/app/schemas/auth.py`（LoginRequest: identifier+password+remember_me, LoginResponse: status+message+user, ErrorResponse: status+error_code+message）

- [x] T022 [US1] 实现 AuthService 核心认证逻辑：`backend/src/app/services/auth_service.py`（authenticate_user 方法：查询用户→验证密码→检查锁定状态→更新登录信息→返回用户，含用户名枚举防护）

- [x] T023 [US1] 创建 Session/AccountLock SQLAlchemy ORM 模型：`backend/src/app/models/session.py`（Session: id, user_id FK, access_token_jti, refresh_token_hash, expires_at, revoked; AccountLock: id, user_id FK, locked_at, unlock_at, failed_attempts, lock_reason, released_at, released_by）

- [x] T024 [US1] 实现会话管理服务：`backend/src/app/services/auth_service.py`（create_session 方法：生成 access_token + refresh_token，存储 refresh_token 哈希到 Session 表，设置 httpOnly Secure SameSite=Lax Cookie）

- [x] T025 [US1] 实现登录端点：`backend/src/app/api/auth.py`（POST /api/auth/login：解析请求→调用 AuthService.authenticate→创建会话→返回响应+Set-Cookie，含速率限制注解）

- [x] T026 [US1] 实现登出端点：`backend/src/app/api/auth.py`（POST /api/auth/logout：清除 Cookie，设置 Session.revoked=True，记录登出事件）

- [x] T027 [US1] 实现令牌刷新端点：`backend/src/app/api/auth.py`（POST /api/auth/refresh：验证 refresh_token→轮换令牌（撤销旧+发放新）→返回新 Cookie）

- [x] T028 [US1] 实现当前用户信息端点：`backend/src/app/api/auth.py`（GET /api/auth/me：从 Cookie 解析 JWT 获取 user_id→查询 User→返回用户信息）

- [x] T029 [P] [US1] 实现 FastAPI 依赖注入：`backend/src/app/api/deps.py`（get_db：异步 session 生成器; get_current_user：从 Cookie 解析 JWT 验证并返回当前用户对象）

- [x] T030 [P] [US1] 创建登录页 Jinja2 模板：`backend/frontend/templates/login.html`（邮箱+密码表单+记住我复选框+登录按钮，含错误消息展示区域，符合 WCAG 2.2 AA）

- [x] T030 [US1] 配置路由挂载：`backend/src/app/api/__init__.py`（注册 auth 路由，挂载到 FastAPI app）

**Checkpoint**: 用户可登录、登出、刷新令牌、查看个人信息，独立可测试

---

## Phase 4: User Story 2 - 系统自动记录登录信息 (Priority: P2)

**Goal**: 每次登录尝试（成功+失败）自动记录完整信息，包括时间、IP、设备、浏览器、结果

**Independent Test**: 用户执行登录后，数据库中自动生成 LoginRecord 记录；管理员可验证记录的字段完整性；异地登录被正确标记

### Tests for User Story 2 ⚠️

- [x] T032 [P] [US2] 编写 LoginRecordService 单元测试：`backend/tests/unit/test_login_record_service.py` — 验证成功/失败登录记录创建、字段填充、is_anomalous 标记逻辑

- [x] T033 [P] [US2] 编写用户代理解析单元测试：`backend/tests/unit/test_user_agent.py` — 验证从 UA 字符串正确解析设备类型、浏览器、操作系统

- [x] T034 [US2] 编写登录记录创建集成测试：`backend/tests/integration/test_login_record_creation.py` — 验证登录端点调用后数据库中存在对应记录

### Implementation

- [x] T035 [P] [US2] 创建 LoginRecord SQLAlchemy ORM 模型：`backend/src/app/models/login_record.py`（id, user_id FK nullable, login_time, ip_address, device_type, browser, operating_system, status enum, failure_reason nullable, is_anomalous, ip_geo_location nullable，含加密存储字段标记）

- [x] T036 [P] [US2] 创建 Pydantic 登录记录 Schema：`backend/src/app/schemas/login_record.py`（LoginRecordResponse, LoginRecordListResponse 含 pagination）

- [x] T037 [US2] 实现用户代理解析服务：`backend/src/app/services/user_agent_service.py`（解析 Request header 中的 User-Agent 字符串，返回 device_type + browser + operating_system）

- [x] T038 [US2] 实现登录记录服务：`backend/src/app/services/login_record_service.py`（create_login_record 方法：获取 IP + 解析 UA + 判断异地登录 + 创建 LoginRecord 持久化）

- [x] T039 [US2] 实现异地登录检测逻辑：`backend/src/app/services/login_record_service.py`（compare_login_location 方法：对比当前 IP 与用户最近 10 次登录的 IP 归属地，不一致则标记 is_anomalous=True）

- [x] T040 [US2] 实现登录记录中间件/依赖注入：`backend/src/app/middleware/login_logger.py`（ASGI 中间件或 FastAPI 依赖，在登录端点响应后自动调用 create_login_record）

- [x] T041 [US2] 集成登录记录到登录端点：修改 `backend/src/app/api/auth.py` 的 POST /login 和 POST /logout，确保每次调用后都生成 LoginRecord

- [x] T042 [US2] 生成 Alembic 自动迁移脚本：运行 `alembic revision --autogenerate -m "add login_record table"`，验证迁移文件包含 LoginRecord 表定义

**Checkpoint**: 所有登录尝试都被记录，含 IP、设备、浏览器信息，异地登录被标记

---

## Phase 5: User Story 3 - 用户查看自己的登录历史 (Priority: P3)

**Goal**: 用户可在个人中心查看自己的登录记录列表（分页、脱敏），按时间倒序

**Independent Test**: 用户登录后访问 /login-history 页面，显示自己的登录记录列表；IP 地址脱敏展示；分页功能正常

### Tests for User Story 3 ⚠️

- [x] T043 [P] [US3] 编写登录历史查询集成测试：`backend/tests/integration/test_login_history.py` — 验证 GET /api/auth/login-history 返回当前用户的记录、IP 脱敏、分页正确

### Implementation

- [x] T044 [US3] 实现用户登录历史查询端点：`backend/src/app/api/login_record.py`（GET /api/auth/login-history：从 JWT 获取当前用户 ID→查询其 LoginRecord→IP 脱敏→分页返回）

- [x] T045 [US3] 实现 IP 脱敏工具函数：`backend/src/app/utils/ip_mask.py`（mask_ip_address：将 IPv4 后两段替换为 ●，IPv6 后 80 位替换）

- [x] T046 [P] [US3] 创建登录历史页 Jinja2 模板：`backend/frontend/templates/login_history.html`（登录记录列表表格，含时间、设备、IP（脱敏）、状态列，分页导航）

- [x] T047 [US3] 在个人中心导航中添加登录历史链接：`backend/frontend/templates/base.html`（导航栏添加"登录历史"菜单项）

**Checkpoint**: 用户可独立查看自己的登录历史，与其他 Story 无关

---

## Phase 6: User Story 4 - 管理员查看与管理登录记录 (Priority: P3)

**Goal**: 管理员可查看全体用户登录记录，支持多维度筛选（用户、时间、IP、结果），识别异常登录模式

**Independent Test**: 管理员进入管理后台，使用筛选条件查询登录记录，返回精确匹配的结果列表

### Tests for User Story 4 ⚠️

- [x] T048 [P] [US4] 编写管理员查询端点集成测试：`backend/tests/integration/test_admin_login_records.py` — 验证 GET /api/admin/login-records 需要管理员权限、筛选参数生效、非管理员返回 403

### Implementation

- [x] T049 [US4] 实现管理员权限依赖：`backend/src/app/api/deps.py`（get_current_admin_user：基于 get_current_user 验证用户是否具有 admin 角色）

- [x] T050 [US4] 实现管理员登录记录查询端点：`backend/src/app/api/login_record.py`（GET /api/admin/login-records：管理员权限校验→多条件筛选查询（user_id、username、email、start_time、end_time、status、ip_address、is_anomalous）→分页返回，IP 不脱敏）

- [x] T051 [US4] 实现复杂筛选查询构建器：`backend/src/app/services/login_record_service.py`（build_query 方法：动态构建 SQLAlchemy 查询，支持时间范围过滤、状态过滤、IP 精确匹配、用户搜索）

- [x] T052 [P] [US4] 创建管理员登录记录页 Jinja2 模板：`backend/frontend/templates/admin/login_records.html`（筛选表单+记录列表表格+分页导航，含异常登录高亮标识）

- [x] T053 [US4] 配置管理路由：`backend/src/app/api/__init__.py`（注册 admin 路由，挂载 login_record 路由，添加 admin role 权限检查）

**Checkpoint**: 管理员可独立使用筛选功能查看全体用户登录记录

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: 影响多个 User Story 的改进

- [x] T054 [P] 编写 E2E 测试（Playwright）：`backend/tests/e2e/test_full_login.py` — 完整浏览器登录流程：打开登录页→输入凭证→点击登录→验证跳转→验证 Cookie 设置

- [x] T055 [P] 编写 E2E 测试（Playwright）：`backend/tests/e2e/test_admin_dashboard.py` — 管理员登录→访问管理后台→筛选登录记录→验证结果

- [x] T056 运行全量测试套件，确保覆盖率达标（核心业务 100%、核心服务 90%+、UI 60-70%）：`pytest --cov=backend/src/app --cov-report=html`

- [x] T057 运行安全扫描：`bandit -r backend/src/app/`（SAST）+ `pip-audit`（SCA），修复所有 Critical/High

- [x] T058 运行代码格式化：`ruff format backend/src/ backend/tests/`

- [x] T059 运行 Lint 检查：`ruff check backend/src/ backend/tests/`，修复所有 violation

- [x] T060 编写 OpenAPI 文档验证：`GET /docs` 确认所有端点都有正确的 Schema 描述和示例

- [x] T061 更新 `backend/README.md`：项目概述、本地开发指南（引用 quickstart.md）、API 文档

- [x] T062 验证 quickstart.md：按照 quickstart.md 的步骤从零搭建环境并运行登录系统

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 无依赖 — 可立即开始
- **Foundational (Phase 2)**: 依赖 Setup 完成 — **阻塞**所有 User Story
- **User Story 1 (Phase 3)**: 依赖 Foundational 完成 — 无其他 Story 依赖
- **User Story 2 (Phase 4)**: 依赖 Foundational 完成 — 依赖 US1 的登录端点（用于集成记录）
- **User Story 3 (Phase 5)**: 依赖 Foundational 完成 — 依赖 US2 的 LoginRecord 模型
- **User Story 4 (Phase 6)**: 依赖 Foundational 完成 — 依赖 US2 的 LoginRecord 模型
- **Polish (Phase 7)**: 依赖所有目标 User Story 完成

### User Story Dependencies

```
Phase 1 (Setup) → Phase 2 (Foundational) →
                                    ├── Phase 3 (US1 - P1) [MVP] ──┐
                                    ├── Phase 4 (US2 - P2) ────────┤
                                    ├── Phase 5 (US3 - P3) ────────┤  (US3, US4 依赖 US2)
                                    └── Phase 6 (US4 - P3) ────────┘
                                                   ↓
                                        Phase 7 (Polish)
```

### Within Each User Story

- 测试（如包含）必须在实现之前编写，且确保失败
- Model 在 Service 之前
- Service 在 Endpoint 之前
- 核心实现在集成之前
- Story 完成后再进入下一优先级

### Parallel Opportunities

- Phase 1: T004 + T006 + T007 + T008 可并行（不同文件）
- Phase 2: T009 + T010 + T011 测试可并行编写；T013 + T014 + T015 可并行实现
- Phase 3: T020 + T021 可并行（Model + Schema）；T025 + T026 + T027 + T028 端点可并行（不同 HTTP 方法）
- Phase 4: T032 + T033 测试可并行；T035 + T036 可并行
- Phase 5: T043 测试 + T046 前端可并行
- Phase 6: T048 测试 + T052 前端可并行
- Phase 7: T054 + T055 E2E 测试可并行编写；T057 + T058 + T059 可并行

---

## Parallel Example: User Story 1

```bash
# 并行运行所有 US1 测试编写：
Task: "编写 AuthService.authenticate 单元测试 (T017)"
Task: "编写 User 创建 fixture 测试 (T018)"

# 并行编写 US1 模型和 Schema：
Task: "创建 User ORM 模型 (T020)"
Task: "创建登录 Pydantic Schema (T021)"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. 完成 Phase 1: Setup
2. 完成 Phase 2: Foundational（CRITICAL — 阻塞所有 Story）
3. 完成 Phase 3: User Story 1（用户可登录、登出、刷新令牌）
4. **停止并验证**: 端到端测试登录流程
5. 如果通过，可部署/Demo

### Incremental Delivery

1. Setup + Foundational → 基础设施就绪
2. 添加 User Story 1 → 独立测试 → 部署/Demo（MVP!）
3. 添加 User Story 2 → 独立测试 → 登录记录就绪
4. 添加 User Story 3 → 独立测试 → 用户可查看历史
5. 添加 User Story 4 → 独立测试 → 管理员审计就绪
6. 每个 Story 添加价值，不破坏之前的 Story

### Parallel Team Strategy

多开发者协作：

1. 团队完成 Setup + Foundational
2. Foundational 完成后：
   - 开发者 A: User Story 1（登录 + 会话管理）
   - 开发者 B: User Story 2 + 3（登录记录 + 用户历史）
   - 开发者 C: User Story 4（管理员审计）
3. 各 Story 独立完成后整合

---

## Notes

- [P] 标记的任务 = 不同文件，无依赖，可并行
- [US#] 标签将任务映射到具体 User Story 以便追溯
- 每个 User Story 应可独立编译、测试、交付
- 宪章强制要求：测试先行（Red-Green-Refactor），覆盖率达标后合入
- 每次 Task 完成或逻辑完成后 commit
- 在任何 Checkpoint 停止可验证 Story 的独立性
- 避免：模糊任务、同文件冲突、跨 Story 依赖破坏独立性

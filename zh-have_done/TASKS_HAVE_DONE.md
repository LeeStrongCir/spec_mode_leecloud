# /speckit.tasks 完整演示示例

> 本文件记录 `/speckit.tasks` 命令对 `005-login-system` 功能的完整执行流程和产出。

---

## 触发命令

```
/speckit.tasks
```

**前置条件**: `specs/005-login-system/` 下已有完整的 spec.md、plan.md、research.md、data-model.md、contracts/、quickstart.md。

---

## Step 1: Setup — 运行配置脚本

```bash
cd /mnt/d/project_workspace/spec_mode_leecloud && bash .specify/scripts/bash/setup-tasks.sh --json
```

**输出**:

```json
{
  "FEATURE_DIR": "/mnt/d/project_workspace/spec_mode_leecloud/specs/005-login-system",
  "AVAILABLE_DOCS": ["research.md", "data-model.md", "contracts/", "quickstart.md"],
  "TASKS_TEMPLATE": "/mnt/d/project_workspace/spec_mode_leecloud/.specify/templates/tasks-template.md"
}
```

---

## Step 2: Pre-Execution — Hook 检查

读取 `.specify/extensions.yml` 中的 `hooks.before_tasks`：

```yaml
before_tasks:
  - extension: git
    command: speckit.git.commit
    enabled: true
    optional: true
    prompt: Commit outstanding changes before task generation?
    description: Auto-commit before task generation
```

**可选钩子**输出：

> ## Extension Hooks
>
> **Optional Pre-Hook**: git
> Command: `/speckit.git.commit`
> Description: Auto-commit before task generation
> Prompt: Commit outstanding changes before task generation?
> To execute: `/speckit.git.commit`

---

## Step 3: Load Design Documents

从 `FEATURE_DIR` 读取以下文档：

| 文档 | 状态 | 作用 |
|------|------|------|
| `spec.md` | ✅ 必需 | 4 个 User Story + 优先级（P1/P2/P3/P3） |
| `plan.md` | ✅ 必需 | 技术栈（Python/FastAPI/SQLAlchemy/Argon2id）、项目结构 |
| `data-model.md` | ✅ 可选 | 4 个实体（User, LoginRecord, Session, AccountLock）+ 关系图 |
| `contracts/` | ✅ 可选 | auth-api.md（4 端点）+ login-record-api.md（2 端点） |
| `research.md` | ✅ 可选 | 9 项技术决策（框架、认证模式、密码哈希、数据库等） |
| `quickstart.md` | ✅ 可选 | 本地开发环境搭建指南 |

---

## Step 4: Execute Task Generation Workflow

### 4a. 提取 User Stories（从 spec.md）

| Story | 优先级 | 内容 |
|-------|--------|------|
| **US1** | P1 | 用户通过凭证登录系统（MVP） |
| **US2** | P2 | 系统自动记录登录信息 |
| **US3** | P3 | 用户查看自己的登录历史 |
| **US4** | P3 | 管理员查看与管理登录记录 |

### 4b. 实体映射（从 data-model.md）

| 实体 | 首次出现的 Story | 原因 |
|------|-----------------|------|
| User | US1 | 登录认证核心实体 |
| Session/Token | US1 | 会话管理 |
| AccountLock | US1 | 登录失败锁定 |
| LoginRecord | US2 | 登录信息记录 |

### 4c. 接口契约映射（从 contracts/）

| 契约 | 端点 | 所属 Story |
|------|------|-----------|
| auth-api.md | POST /api/auth/login | US1 |
| auth-api.md | POST /api/auth/logout | US1 |
| auth-api.md | POST /api/auth/refresh | US1 |
| auth-api.md | GET /api/auth/me | US1 |
| login-record-api.md | GET /api/auth/login-history | US3 |
| login-record-api.md | GET /api/admin/login-records | US4 |

### 4d. 宪章要求分析

根据《软件测试宪章》，本功能属 **HIGH 风险等级**（认证模块变更）：
- **必须** 执行 TDD（测试先行）
- 核心业务逻辑覆盖率目标：**100%**
- 核心服务覆盖率目标：**90%+**
- UI 组件覆盖率目标：**60-70%**

因此 **所有 User Story 阶段都包含测试任务**。

---

## Step 5: Generate tasks.md

根据 tasks-template.md 模板，生成实际的 `specs/005-login-system/tasks.md`：

### Phase 1: Setup (8 任务)

项目初始化和基础结构搭建：
- T001 创建后端项目目录结构
- T002 初始化 `pyproject.toml` 生产依赖
- T003 初始化 `pyproject.toml` 开发依赖
- T004 [P] 配置代码质量工具（ruff、.python-version）
- T005 [P] 初始化 Alembic
- T006 创建 `.env.example`
- T007 [P] 创建 `__init__.py` 和 `config.py`
- T008 [P] 创建 `main.py`（FastAPI 应用入口）

### Phase 2: Foundational (8 任务)

所有 User Story 的核心基础设施，**阻塞**任何 User Story 工作：
- T009 [P] 编写 Database 连接单元测试
- T010 [P] 编写 JWT Token 单元测试
- T011 [P] 编写 Password Hash 单元测试
- T012 创建数据库异步引擎和会话工厂
- T013 实现 JWT 工具模块
- T014 实现密码哈希服务
- T015 实现 CSRF 保护配置
- T016 创建全局异常处理中间件

**Checkpoint**: 数据库连接、JWT 令牌、密码哈希、CSRF 保护、异常处理全部就绪

### Phase 3: User Story 1 - 用户通过凭证登录系统 (P1, 15 任务) 🎯 MVP

| 类型 | 任务 ID | 内容 |
|------|---------|------|
| Test | T017 [P] | 编写 AuthService.authenticate 单元测试 |
| Test | T018 [P] | 编写 User 创建 fixture 测试 |
| Test | T019 | 编写登录端点集成测试 |
| Model | T020 [P] | 创建 User ORM 模型 |
| Schema | T021 [P] | 创建 Pydantic 登录请求/响应 Schema |
| Service | T022 | 实现 AuthService 核心认证逻辑 |
| Model | T023 | 创建 Session/AccountLock ORM 模型 |
| Service | T024 | 实现会话管理服务 |
| Endpoint | T025 | 实现登录端点（POST /api/auth/login） |
| Endpoint | T026 | 实现登出端点（POST /api/auth/logout） |
| Endpoint | T027 | 实现令牌刷新端点（POST /api/auth/refresh） |
| Endpoint | T028 | 实现当前用户信息端点（GET /api/auth/me） |
| Deps | T029 [P] | 实现 FastAPI 依赖注入 |
| UI | T030 [P] | 创建登录页 Jinja2 模板 |
| Config | T031 | 配置路由挂载 |

**Checkpoint**: 用户可登录、登出、刷新令牌、查看个人信息，独立可测试

### Phase 4: User Story 2 - 系统自动记录登录信息 (P2, 11 任务)

| 类型 | 任务 ID | 内容 |
|------|---------|------|
| Test | T032 [P] | 编写 LoginRecordService 单元测试 |
| Test | T033 [P] | 编写用户代理解析单元测试 |
| Test | T034 | 编写登录记录创建集成测试 |
| Model | T035 [P] | 创建 LoginRecord ORM 模型 |
| Schema | T036 [P] | 创建 Pydantic 登录记录 Schema |
| Service | T037 | 实现用户代理解析服务 |
| Service | T038 | 实现登录记录服务 |
| Service | T039 | 实现异地登录检测逻辑 |
| Middleware | T040 | 实现登录记录中间件/依赖注入 |
| Integration | T041 | 集成登录记录到登录端点 |
| Migration | T042 | 生成 Alembic 自动迁移脚本 |

**Checkpoint**: 所有登录尝试都被记录，含 IP、设备、浏览器信息，异地登录被标记

### Phase 5: User Story 3 - 用户查看自己的登录历史 (P3, 5 任务)

| 类型 | 任务 ID | 内容 |
|------|---------|------|
| Test | T043 [P] | 编写登录历史查询集成测试 |
| Endpoint | T044 | 实现用户登录历史查询端点（GET /api/auth/login-history） |
| Utils | T045 | 实现 IP 脱敏工具函数 |
| UI | T046 [P] | 创建登录历史页 Jinja2 模板 |
| UI | T047 | 在个人中心导航中添加登录历史链接 |

**Checkpoint**: 用户可独立查看自己的登录历史，与其他 Story 无关

### Phase 6: User Story 4 - 管理员查看与管理登录记录 (P3, 6 任务)

| 类型 | 任务 ID | 内容 |
|------|---------|------|
| Test | T048 [P] | 编写管理员查询端点集成测试 |
| Deps | T049 | 实现管理员权限依赖（get_current_admin_user） |
| Endpoint | T050 | 实现管理员登录记录查询端点（GET /api/admin/login-records） |
| Service | T051 | 实现复杂筛选查询构建器 |
| UI | T052 [P] | 创建管理员登录记录页 Jinja2 模板 |
| Config | T053 | 配置管理路由 |

**Checkpoint**: 管理员可独立使用筛选功能查看全体用户登录记录

### Phase 7: Polish & Cross-Cutting Concerns (9 任务)

- T054 [P] 编写 E2E 测试（Playwright）：完整浏览器登录流程
- T055 [P] 编写 E2E 测试（Playwright）：管理员 Dashboard
- T056 运行全量测试套件，确保覆盖率达标
- T057 运行安全扫描：bandit（SAST）+ pip-audit（SCA）
- T058 运行代码格式化：`ruff format`
- T059 运行 Lint 检查：`ruff check`
- T060 编写 OpenAPI 文档验证
- T061 更新 `backend/README.md`
- T062 验证 quickstart.md

---

## Step 6: Report — 输出汇总

### 任务统计

| 指标 | 数据 |
|------|------|
| **总任务数** | **62** |
| **并行任务** | 25 个（含 [P] 标记） |
| **Phase 1: Setup** | 8 任务 |
| **Phase 2: Foundational** | 8 任务（3 测试 + 5 实现） |
| **Phase 3: US1 (P1) MVP** | 15 任务（3 测试 + 12 实现） |
| **Phase 4: US2 (P2)** | 11 任务（3 测试 + 8 实现） |
| **Phase 5: US3 (P3)** | 5 任务（1 测试 + 4 实现） |
| **Phase 6: US4 (P3)** | 6 任务（1 测试 + 5 实现） |
| **Phase 7: Polish** | 9 任务 |

### 各 Story 独立测试标准

| Story | 内容 | 独立测试方式 |
|-------|------|-------------|
| **US1 (P1)** | 用户通过凭证登录系统 | 输入正确凭证可登录并获得有效 Cookie，错误凭证被拒绝 |
| **US2 (P2)** | 系统自动记录登录信息 | 登录后数据库自动生成 LoginRecord，字段完整 |
| **US3 (P3)** | 用户查看自己的登录历史 | 用户访问 /login-history 页面显示自己的记录，IP 脱敏 |
| **US4 (P3)** | 管理员查看与管理登录记录 | 管理员使用筛选条件查询，返回精确匹配结果列表 |

### 依赖关系图

```
Phase 1 (Setup) → Phase 2 (Foundational) →
                                    ├── Phase 3 (US1 - P1) [MVP] ──┐
                                    ├── Phase 4 (US2 - P2) ────────┤
                                    ├── Phase 5 (US3 - P3) ────────┤  (US3, US4 依赖 US2)
                                    └── Phase 6 (US4 - P3) ────────┘
                                                   ↓
                                        Phase 7 (Polish)
```

### 格式验证

| 检查项 | 状态 |
|--------|------|
| 所有任务以 `- [ ]` 开头 | ✅ |
| 所有任务含 Task ID (T001-T062) | ✅ |
| User Story 任务含 [US#] 标签 | ✅ |
| 所有任务含精确文件路径 | ✅ |
| [P] 标记仅限并行任务 | ✅ |
| 任务编号连续无重复 | ✅ |

---

## Step 7: after_tasks Hook 检查

读取 `extensions.yml` 的 `hooks.after_tasks`：

```yaml
after_tasks:
  - extension: git
    command: speckit.git.commit
    enabled: true
    optional: true
```

输出：

> ## Extension Hooks
>
> **Optional Hook**: git
> Command: `/speckit.git.commit`
> Description: Auto-commit after task generation
> To execute: `/speckit.git.commit`

---

## 最终产出文件

```
specs/005-login-system/
├── spec.md              # Feature specification (from /speckit.specify)
├── plan.md              # Implementation plan (from /speckit.plan)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
├── tasks.md             # Phase 2 output (from /speckit.tasks) ← 本次产出
└── checklists/
    └── requirements.md  # Quality checklist
```

---

## 实施策略

### MVP First (仅 User Story 1)

1. Phase 1: Setup → 项目初始化
2. Phase 2: Foundational → 基础设施就绪（**CRITICAL，阻塞所有 Story**）
3. Phase 3: User Story 1 → 用户可登录/登出/刷新令牌
4. **停止并验证**: 端到端测试登录流程
5. 部署/Demo

### Incremental Delivery

1. Setup + Foundational → 基础设施就绪
2. 添加 US1 → 独立测试 → 部署/Demo（**MVP!**）
3. 添加 US2 → 独立测试 → 登录记录就绪
4. 添加 US3 → 独立测试 → 用户可查看历史
5. 添加 US4 → 独立测试 → 管理员审计就绪
6. Phase 7: Polish → 全量质量保障
7. 每个 Story 添加价值，不破坏之前的 Story

### Parallel Team Strategy

多开发者协作：
1. 团队完成 Setup + Foundational
2. Foundational 完成后：
   - 开发者 A: US1（登录 + 会话管理）
   - 开发者 B: US2 + US3（登录记录 + 用户历史）
   - 开发者 C: US4（管理员审计）
3. 各 Story 独立完成后整合

---

## 下一步

```
/speckit.implement — 按 tasks.md 逐条实施，从 Phase 1 开始
```

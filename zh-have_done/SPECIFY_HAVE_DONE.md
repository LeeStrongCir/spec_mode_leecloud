# /speckit.specify 完整演示示例

> 本文件记录 `/speckit.specify` 命令对一个真实功能需求的完整执行流程和产出。

---

## 触发命令

```
/speckit.specify 为系统创建登录功能，并记录登录信息
```

---

## Step 1: 生成短名称 + 提取关键概念

**短名称**: `login-system` (2 words, action-noun format)

**关键概念提取**:

| 维度 | 内容 |
|------|------|
| **Actors** | 普通用户（登录操作）、管理员（查看审计记录） |
| **Actions** | 凭证登录、登出、自动记录登录信息、查看登录历史、多维度筛选、暴力破解防护 |
| **Data** | 用户实体、登录记录、会话/令牌、账号锁定记录 |
| **Constraints** | 宪章要求 HIGH 风险等级认证模块、TDD 100% 覆盖率、OWASP 安全标准、PII 加密存储 |

---

## Step 2: Pre-Execution — Extension Hook 检查

读取 `.specify/extensions.yml` 中的 `hooks.before_specify`：

```yaml
before_specify:
  - extension: git
    command: speckit.git.feature
    enabled: true
    optional: false
    prompt: Execute speckit.git.feature?
    description: Create feature branch before specification
    condition: null
```

这是 **mandatory** 钩子，系统输出：

> ## Extension Hooks
>
> **Automatic Pre-Hook**: git
> Executing: `/speckit.git.feature`
>
> Wait for the result of the hook command before proceeding to the Outline.

钩子执行后创建/切换到 feature branch（如 `001-login-system`）。

---

## Step 3: 确定 Feature 目录

项目配置 `.specify/init-options.json` 中 `branch_numbering: "sequential"`，扫描 `specs/` 已有目录后取下一个序号：

- 已有目录: `specs/004-audit-log/`
- 下一个序号: `005`
- **目录**: `specs/005-login-system/`
- **文件**: `specs/005-login-system/spec.md`

```bash
mkdir -p specs/005-login-system/checklists
cp .specify/templates/spec-template.md specs/005-login-system/spec.md
```

写入 `.specify/feature.json`:

```json
{
  "feature_directory": "specs/005-login-system"
}
```

---

## Step 4-6: 探索性研究 (Parallel)

同时发起后台 explore agent 调研，了解项目上下文：

### Explore Agent 1: 项目结构分析

| 发现 | 结论 |
|------|------|
| 无任何应用代码 | greenfield 项目，从零开始 |
| Git 历史 | 仅一次 "Initial commit" |
| 已有 spec | `004-audit-log` 假设"系统已存在认证和权限管理体系" |
| 测试宪章 | constitution.md 定义 TDD、覆盖率、安全测试、CI/CD Gate 等标准 |
| 技术栈 | 未定义，将在 `/speckit.plan` 阶段决定 |
| 依赖文件 | 仅 `.opencode/package.json`（工具链依赖） |

### Explore Agent 2: 项目配置分析

| 发现 | 结论 |
|------|------|
| init-options.json | AI = opencode, branch_numbering = sequential, script = sh |
| AGENTS.md | 指向当前 plan.md 作为技术细节参考 |
| README.md | 仅项目名称 "spec_mode_leecloud" |
| VSCode settings | Speckit 命令推荐已配置 |

---

## Step 7: 编写 Spec 文件

根据 spec-template.md 模板和用户描述，生成完整 `specs/005-login-system/spec.md`：

```markdown
# Feature Specification: 用户登录与登录信息记录

**Feature Branch**: `001-login-system`
**Created**: 2026-05-06
**Status**: Draft
**Input**: User description: "为系统创建登录功能，并记录登录信息"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 用户通过凭证登录系统 (Priority: P1)

用户打开系统访问入口，输入身份凭证（用户名/邮箱和密码），系统验证通
过后授予访问权限，并自动记录本次登录的详细信息。登录成功用户可以正
常操作系统的各项功能。

**Why this priority**: 这是整个系统的门户——如果没有登录功能，系统无法
识别用户身份，更谈不上安全访问控制。一切后续功能都依赖于此。本项目的
`004-audit-log` spec 已明确假设"系统已存在用户认证和权限管理体系"，因此
本功能是其必要前置依赖。

**Independent Test**: 用户输入有效凭证后能够成功进入系统主页；输入无效凭
证后被拒绝并得到明确的错误提示。整个登录流程可独立运行且不依赖其他功能。

**Acceptance Scenarios**:

1. **Given** 用户在登录页面, **When** 输入正确的用户名和密码并点击登录,
   **Then** 系统验证通过，跳转至用户首页并生成成功的登录记录
2. **Given** 用户在登录页面, **When** 输入错误的密码, **Then** 系统拒绝登录
   并显示"用户名或密码错误"提示，同时生成失败的登录尝试记录
3. **Given** 用户在登录页面, **When** 输入不存在的用户名, **Then** 系统拒绝
   登录并显示"用户名或密码错误"提示（与密码错误相同的提示内容，避免用户名
   枚举攻击）
4. **Given** 用户已登录且在有效会话期内, **When** 再次访问系统, **Then** 系
   统自动识别用户身份，无需重新登录

---

### User Story 2 - 系统自动记录登录信息 (Priority: P2)

每次用户尝试登录时，无论成功或失败，系统都会自动记录完整的登录信息，
包括时间、来源IP、使用的设备/浏览器信息、登录结果等。这些登录记录可供
用户本人和管理员后续查看。

**Why this priority**: 登录信息记录是安全审计的基础能力。没有记录，就无
法追踪账号异常登录、安全风险识别以及合规性检查。

**Independent Test**: 用户执行登录后，系统内部生成对应的登录信息记录；管
理员可在后台查看该记录的所有字段信息，验证数据的完整性和准确性。

**Acceptance Scenarios**:

1. **Given** 用户成功登录, **When** 登录完成, **Then** 系统生成一条包含录时
   间、IP地址、设备信息、登录状态（成功）的登录记录
2. **Given** 用户登录失败, **When** 登录被拒绝, **Then** 系统生成一条包含
   登录时间、IP地址、失败原因、登录状态（失败）的登录记录
3. **Given** 用户异地登录（非常用IP地址）, **When** 登录成功, **Then** 系统
   标记该登录为"异地登录"并记录IP归属地信息
4. **Given** 同一IP短时间连续登录失败超过阈值, **When** 失败次数达到限制,
   **Then** 系统锁定该IP的登录尝试并生成安全告警记录

---

### User Story 3 - 用户查看自己的登录历史 (Priority: P3)

用户可以查看自己的最近登录记录列表，包括每次登录的时间、设备、IP地址和
登录结果。用户可通过登录历史识别异常登录行为，增强账号安全意识。

**Why this priority**: 为用户提供账号安全的可见性，是提升用户体验和信任
度的一部分。属于锦上添花的功能，不影响核心使用流程。

**Independent Test**: 用户进入"我的登录历史"页面，系统展示其最近10条登录
记录；用户可以逐条查看每条记录的详细信息。

**Acceptance Scenarios**:

1. **Given** 用户在个人中心, **When** 点击"登录历史"单, **Then** 系统展
   示该用户最近的登录记录列表，按时间倒序排列
2. **Given** 用户查看登录历史列表, **When** 点击某条记录, **Then** 系统展示
   该次登录的详细信息（包括时间精确到秒、完整IP地址、设备类型、浏览器版
   本等）
3. **Given** 用户的登录历史超过100条, **When** 查看列表, **Then** 系统支持
   分页浏览，默认显示最近的10条

---

### User Story 4 - 管理员查看与管理登录记录 (Priority: P3)

管理员可以在系统管理界面查看全体用户的登录记录，支持按用户、时间范围、
IP地址、登录结果等多维度筛选。管理员可以识别异常的登录模式并采取相应
安全措施。

**Why this priority**: 对于企业级应用或需要合规管理的场景，管理员的登录审
计能力至关重要。但在MVP阶段优先级低于用户自身登录功能。

**Independent Test**: 管理员进入管理后台，查看登录记录列表，使用不同的筛
选条件组合询特定的登录记录集合。

**Acceptance Scenarios**:

1. **Given** 管理员进入登录管理页面, **When** 查看所有记录, **Then** 系统展
   示所有用户的登录记录概要
2. **Given** 管理员进行筛选查询, **When** 设置用户、时间范围、IP等条件,
   **Then** 系统返回精确匹配的结果列表
3. **Given** 管理员发现某账号存在大量失败登录尝试, **When** 点击该账号,
   **Then** 系统展示详细的登录失败记录并提示可能的安全风险

---

### Edge Cases

- 用户连续输入错误密码超过次数限制时，账号将被临时锁定，锁定时长和解锁方式待定
- 用户在多地多设备同时登录时，系统允许多设备并发，但会记录每个设备信息
- 登录信息记录的存储容量达到上限时，采用归档策略，超出保留周期的历史数据转移至冷存储
- 登录记录中的个人敏感信息（IP地址、设备信息）遵循数据保护法规进行加密存储
- 系统遭暴力破解攻击时，结合 IP 级别限制、验证码机制、渐进式延迟等防御手段

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 系统 MUST 提供用户登录入口页面，包含用户名/邮箱输入框、密码输入框和登录按钮
- **FR-002**: 系统 MUST 验证用户提交的登录凭证（用户名/邮箱与密码）是否与系统中录的有效凭证匹配
- **FR-003**: 系统 MUST 在凭证验证通过后建立用户会话或颁发访问令牌
- **FR-004**: 系统 MUST 在用户登录成功后将用户重定向至其个人首页或上次访问的页面
- **FR-005**: 系统 MUST 提供用户主动登出功能，清除当前会话或令牌
- **FR-006**: 系统 MUST 在每次登录尝试（无论成功或失败）时自动成一条登录记录
- **FR-007**: 每条登录记录 MUST 包含：记录ID、用户ID（失败登录时可能为空）、登录尝试时间、来源IP地址、设备类型、浏览器信息、操作系统信息、登录结果状态（成功/失败）、失败原因（如有）
- **FR-008**: 对于失败登录，系统 MUST 记录明确的失败因（如密码错误、账号不存在、账号已锁定、账号已禁用）
- **FR-009**: 系统 MUST 标记异地登录行为（用户登录IP地址与常用登录地不一致）
- **FR-010**: 系统 MUST 对同一用户在短时间内的连续登录失败次数进行计数
- **FR-011**: 当用户登录失败次数达到阈值时，系统 MUST 临时锁定该账号的登录功能
- **FR-012**: 用户 MUST 能够在个人中心查看自己的登录历史记录
- **FR-013**: 登录历史记录 MUST 按时间倒序排列，支持分页浏览
- **FR-014**: 管理员 MUST 能够查看全体用户的登录记录
- **FR-015**: 管理员 MUST 能够通过用户名/邮箱、时间范围、IP地址、登录结果状态等多维度条件筛选登录记录
- **FR-016**: 系统 MUST 提供"记住我"功能，允许用户选择延长登录会话有效期
- **FR-017**: 系统 MUST 提供"忘记密码"入口，引导用户进行密码找回操作
- **FR-018**: 登录信息中的敏感数据（IP地址、设备信息）在数据库中 MUST 进行加密存储

### Key Entities

- **用户 (User)**: 系统的使用者，包含唯一用户ID、用户名、邮箱地址、密码哈希、账号状态（正常/锁定/禁用）等属性
- **登录记录 (LoginRecord)**: 一次登录尝试的完整信息，包含记录ID、用户ID、登录时间戳、来源IP地址、设备类型、浏览器信息、操作系统、登录结果状态、失败原因、是否异地登录标记
- **会话/令牌 (Session/Token)**: 用户登录成功后系统建立身份凭证，包含令牌/会话ID、关联用户ID、创建时间、过期时间、刷新令牌（如适用）
- **账号锁定记录 (AccountLock)**: 因连续登录失败而触发的临时安全限制，包含锁定用户ID、开始时间、释放时间（或手动解锁标记）、触发原因

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 用户输入正确凭证后在3秒内完成验证并进入系统（从点击登录到页面跳转完成）
- **SC-002**: 系统可以支持500个用户在同一分钟内并发登录而不出现性能降级
- **SC-003**: 登录功能上线后，未授权访问事件数量降低至零（所有受保护资源强制登录验证）
- **SC-004**: 95%的用户首次尝试登录即成功（无登录失败）
- **SC-005**: 用户能够在2次点击内从进入系统到达个人登录历史页面
- **SC-006**: 暴力破解攻击场景下，系统在5分钟内自动锁定攻击目标，阻止进一步的登录尝试
- **SC-007**: 登录信息记录的完整率达到100%——每次登录尝试都被准确记录，无遗漏

## Assumptions

- 本项目为全新系统（greenfield），不存在已有的用户数据或认证基础设施
- 用户在使用系统前已在系统中注册了有效账号（注册功能作为另一独立 feature 规划）
- 用户具备基本的互联网连接和设备访问能力（桌面浏览器为主要入口）
- 系统的密码存储采用安全的哈希算法（如 bcrypt、Argon2），不会以明文形式保存密码
- "登录信息"包含技术层面的信息（IP、设备、浏览器）和业务层面的信息（登录时间、结果状态），但不包括用户的具体操作行为记录
- 登录功能首期实现以 Web 网页端为主，移动端配视为可选范围
- 根据项目《软件测试宪章》，本功能属于 **HIGH 风险等级**（认证模块变更），必须执行 TDD 开发、100% 核心业务逻辑覆盖率、完整子系统回归测试和关键路径 E2E 验证
- 本功能 `001-login-system` 是 `004-audit-log`（操作审计日志）的前置依赖，完成后将满足审计日志所假设的认证基础设施
```

---

## Step 8: 创建质量检查清单

在 `specs/005-login-system/checklists/requirements.md` 中生成：

```markdown
# Specification Quality Checklist: 用户登录与登录信息记录

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-05-06
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous (18 FRs, all testable)
- [x] Success criteria are measurable (7 SCs with metrics)
- [x] Success criteria are technology-agnostic (no implementation details)
- [x] All acceptance scenarios are defined (4 stories, 12 scenarios)
- [x] Edge cases are identified (5 edge cases documented)
- [x] Scope is clearly bounded (greenfield login system)
- [x] Dependencies and assumptions identified (8 assumptions)

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows (P1 login → P2 recording → P3 history)
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification

## Notes

- All checklist items passed validation
- Spec is ready for `/speckit.plan`
```

---

## Step 9: Report Completion

```
## ✅ /speckit.specify 执行完成

SPECIFY_FEATURE_DIRECTORY: specs/005-login-system
SPEC_FILE: specs/005-login-system/spec.md
Checklist: specs/005-login-system/checklists/requirements.md (17/17 passed)

Spec is ready for /speckit.plan.
```

---

## Step 10: after_specify Hook 检查

读取 `extensions.yml` 的 `hooks.after_specify`：

```yaml
after_specify:
  - extension: git
    command: speckit.git.commit
    enabled: true
    optional: true
    prompt: Commit specification changes?
    description: Auto-commit after specification
```

输出：

> ## Extension Hooks
>
> **Optional Hook**: git
> Command: `/speckit.git.commit`
> Description: Auto-commit after specification
> Prompt: Commit specification changes?
> To execute: `/speckit.git.commit`

---

## 最终产出文件

```
specs/005-login-system/
├── spec.md                          # Feature specification (135 lines)
└── checklists/
    └── requirements.md              # Quality checklist (17/17 passed)
```

## Spec 核心内容汇总

| 章节 | 内容 |
|------|------|
| **4 个 User Story** | P1: 凭证登录 → P2: 自动记录登录信息 → P3: 用户查看自己的登录历史 → P3: 管理员审计 |
| **18 条 Functional Requirements** | 覆盖登录页面、凭证验证、会话管理、登录记录生成、失败处理、异地登录标记、暴力破解防护等 |
| **4 个 Key Entities** | User、LoginRecord、Session/Token、AccountLock |
| **7 条 Success Criteria** | 登录响应 ≤3s、500并发、0未授权访问、95%首次成功率等 |
| **8 条 Assumptions** | 包括对项目宪章的引用、greenfield项目前提、TDD要求等 |
| **5 个 Edge Cases** | 账号锁定、多设备并发、存储归档、敏感数据加密、暴力破解防御 |

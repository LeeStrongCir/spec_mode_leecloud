# 测试计划: [FEATURE]

**分支**: `[###-feature-name]` | **日期**: [DATE] | **关联 Spec**: [链接]
**输入**: 来自 `/specs/[###-feature-name]/spec.md` 的功能规格

**注意**: 本模板回答 spec-kit 工作流中的「怎么测试」问题。与 spec.md（测试什么 + 为什么测）和 plan.md（怎么实现）互补。

## 摘要

[从功能规格提取：测试范围 + 基于技术方案的方法]

## 技术上下文

<!--
  需执行操作：将本节内容替换为本功能测试的技术细节。
  此处的结构仅作指导参考。
-->

**测试框架**: [如 pytest、Jest、cargo test 或 待确认]  
**测试数据库**: [如 SQLite 内存库、test containers 或 不适用]  
**浏览器自动化**: [如 Playwright、Selenium、Cypress 或 不适用]  
**Mock 策略**: [如 unittest.mock、pytest-mock、nock 或 待确认]  

## 宪章门禁

*门禁：必须在测试实现前通过。测试设计后需重新检查。*

[根据宪章文件确定的门禁项]

## 测试环境

<!--
  需执行操作：将本节内容替换为本功能测试所需的具体环境配置。
  此环境同时用于集成测试和 E2E 测试。
-->

### 环境要求

| 组件 | 要求 | 备注 |
|------|------|------|
| **运行时** | [如 Python 3.11+, Node 18+] | 与生产环境保持一致 |
| **数据库** | [如 SQLite 内存库 / PostgreSQL test container] | 每个测试独立实例 |
| **浏览器** | [如 Chromium, Firefox] | E2E 测试需要 |
| **依赖服务** | [如 Redis, Celery worker] | 按需启动 |

### 环境变量配置

```bash
# .env.test - 测试环境专用配置（集成测试 + E2E 共用）
DATABASE_URL=sqlite:///test.db
TESTING=true
SECRET_KEY=test-secret-key-do-not-use-in-production
MOCK_EXTERNAL_SERVICES=true
```

### 测试配置文件

| 文件 | 用途 |
|------|------|
| `tests/conftest.py` | 全局 fixture（DB、用户、客户端） |
| `tests/[feature]/conftest.py` | feature 级 fixture |
| `pytest.ini` / `pyproject.toml` | pytest 配置（标记、并行） |

### 测试数据准备

| 数据类型 | 来源 | 刷新频率 | 清理策略 |
|----------|------|----------|----------|
| 基准测试数据 | [如 factory fixtures, seed scripts] | 每次测试运行前 | 事务回滚自动清理 |
| 用户测试数据 | [如测试账号池, Factory Boy] | 按需创建 | 测试结束后自动删除 |
| 外部服务 Mock 数据 | [如 fixtures/, responses.json] | 手动更新 | 版本控制管理 |

### 环境隔离策略

- **数据库隔离**: 每个测试使用独立的内存数据库或独立的 schema
- **网络隔离**: Mock 外部服务调用，避免真实网络请求
- **状态隔离**: 测试间不共享状态，每个测试从干净的初始状态开始

## 测试策略总览

### 测试层次

<!--
  需执行操作：将下表的占位内容替换为本功能的具体测试层次。删除未使用的层次，并用实际测试文件路径展开。
-->

本功能包含以下测试层次：

| 层级 | 职责 | 覆盖指引 | 失败定位 |
|------|------|----------|----------|
| **Integration（集成）** | 组件协作 + API 契约（Route → Service → DB） | 覆盖关键用户路径，5-15 条用例 | 定位到组件交互边界 |
| **E2E（端到端）** | 完整用户流程端到端验证 | 仅覆盖核心 P1 路径，1-N 条用例 | 定位到用户操作级别 |

### 分层边界规则

- **集成测试**：使用真实数据库（SQLite 内存库或 test containers），**不** mock 框架层（FastAPI、SQLAlchemy），但**可** mock 外部服务（邮件、支付、第三方 API）。
- **E2E 测试**：真实浏览器 + 完整应用栈，仅 mock 不可控的外部依赖。**不复测**集成测试已覆盖的 API 契约。

## 各层测试详细计划

### 集成测试

**目标**：[本功能的组件集成点和 API 契约]

| 集成点 | 测试文件 | 验证范围 |
|--------|----------|----------|
| [API Route → Service → DB] | `tests/integration/test_[flow].py` | 请求 → 响应 → 数据库状态 |
| [中间件 → Auth → Route] | `tests/integration/test_[auth].py` | 认证/授权链路 |
| [异步任务生命周期] | `tests/integration/test_[async].py` | 任务创建、状态轮询、最终一致性 |

#### Mock 策略

| 依赖类型 | 处理方式 | 理由 |
|----------|----------|------|
| 外部 API/服务 | `unittest.mock` / `pytest-mock` | 避免网络不确定性，仅测本功能逻辑 |
| 密码哈希 | 直接调用真实 argon2 | 确定性算法，无外部依赖，不应 mock |
| JWT 签发 | mock 或固定 secret | 签发逻辑不在被测范围内时使用 |
| 时间 | `freezegun` 冻结时间 | 时间相关逻辑需要确定性 |

#### 测试数据隔离

- **Fixture 作用域**: 每个测试使用独立的内存数据库，通过 `pytest.fixture(scope="function")` 保证
- **数据工厂**: 使用 Factory Boy 或自定义 builder 模式创建测试数据
- **事务回滚**: 每个测试在事务中执行，测试完成后自动回滚

### E2E 测试

**目标**：[本功能需要端到端验证的关键用户路径]

| 场景 | 测试文件 | 路径 | 预期结果 |
|------|----------|------|----------|
| [关键路径 1] | `tests/e2e/test_[scenario].py` | 用户操作序列 → 最终页面状态 | [可验证的结果] |
| [关键路径 2] | `tests/e2e/test_[scenario].py` | 用户操作序列 → 最终页面状态 | [可验证的结果] |

#### Playwright 策略

- **页面交互**: 优先使用 `data-testid` 定位元素
- **状态验证**: 验证 URL、页面内容、DOM 属性变化、网络请求
- **等待策略**: 使用 Playwright 自动等待，避免硬编码 sleep
- **视觉回归**: [是否需要截图对比]

#### E2E 测试范围约束

- E2E **不复测** 集成测试已验证的接口契约和边界条件
- E2E 仅覆盖「用户操作 → 系统响应」的完整路径
- 每条 E2E 用例必须对应 spec.md 中的一个P1级别用户故事或关键验收场景

## 测试基础设施

### Fixture 设计

<!--
  需执行操作：将下表的占位 fixture 替换为本功能的具体实现。删除未使用的 fixture，并展开为真实实现。
-->

```python
# conftest.py 中的关键 fixture 模板

@pytest.fixture
async def db_session():
    """每个测试独立的内存 SQLite 会话"""
    ...

@pytest.fixture
def test_user(db_session):
    """使用 factory 创建标准用户"""
    ...

@pytest.fixture
def admin_user(db_session):
    """创建管理员用户"""
    ...

@pytest.fixture
def authenticated_client(client, test_user):
    """创建已登录状态的测试客户端"""
    ...

@pytest.fixture
async def async_client():
    """AsyncHTTPClient fixture，用于异步 API 测试"""
    ...
```

### 并行执行策略

- 集成测试可使用 pytest-xdist 并行执行（独立 DB）
- E2E 测试串行执行（避免浏览器实例冲突）

## 测试可追溯性

### FR → Test 映射

| Spec 中的 FR | 测试层级 | 测试文件 | 测试用例 |
|--------------|----------|----------|----------|
| FR-001 | Integration + E2E | `tests/integration/test_[...].py` | [test name] |
| FR-002 | Integration | `tests/integration/test_[...].py` | [test name] |
| FR-003 | Integration | `tests/integration/test_[...].py` | [test name] |

### 用户故事 → Test 映射

| 用户故事 | 优先级 | 对应测试 | 独立验证方式 |
|------------|--------|----------|--------------|
| [用户故事 1 标题] | P1 | [列测试文件] | [如何独立验证] |
| [用户故事 2 标题] | P2 | [列测试文件] | [如何独立验证] |

## 测试风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| [如：异步操作时序不确定性] | [测试结果不确定] | [确定性等待策略，固定时间] |
| [如：外部 API 不可用] | [集成测试失败] | [Mock 外部依赖] |
| [如：数据库状态污染] | [测试间相互影响] | [事务回滚，独立 DB] |

## 复杂度追踪

> **仅在宪章门禁存在需要证明的违反项时填写**

| 违反项 | 为什么需要 | 拒绝更简单方案的理由 |
|--------|-----------|---------------------|
| [如：额外测试层] | [当前需求] | [为什么现有层次不够] |
| [如：自定义测试基础设施] | [具体问题] | [为什么标准 fixture 不够] |

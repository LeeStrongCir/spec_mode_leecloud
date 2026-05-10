---
description: 使用测试计划模板生成本 feature 的「怎么测试」策略文档。
handoffs:
  - label: 生成任务
    agent: speckit.tasks
    prompt: 基于测试计划生成分解的测试任务
    send: true
---

## 用户输入

```text
$ARGUMENTS
```

在继续之前，你**必须**考虑用户输入的内容（如果不为空）。

## 执行前检查

**检查扩展钩子**：
- 检查项目根目录下是否存在 `.specify/extensions.yml`。
- 如果存在，读取它并查找 `hooks.before_test_plan` 键下的条目。
- 如果 YAML 无法解析或无效，静默跳过并正常继续。
- 过滤掉 `enabled` 明确为 `false` 的钩子。没有 `enabled` 字段的钩子默认视为已启用。
- 对于每个可执行的钩子，根据 `optional` 标志输出（参考 speckit.plan.zh-CN.md 的钩子输出格式）。
- 如果没有注册任何钩子，或 `.specify/extensions.yml` 不存在，则静默跳过。

## 大纲

1. **设置**：从仓库根目录运行 `.specify/scripts/bash/setup-plan.sh --json` 并解析 JSON 获取 `FEATURE_SPEC`、`IMPL_PLAN`、`SPECS_DIR`、`BRANCH`。

2. **加载上下文**：
   - 读取 `FEATURE_SPEC`（`specs/[###-feature]/spec.md`）— 获取 User Story、FR、Acceptance Scenarios
   - 读取 `IMPL_PLAN`（`specs/[###-feature]/plan.md`）— 获取技术上下文、项目结构、数据模型
   - 读取 `.specify/memory/constitution.md` — 获取测试门禁要求
   - 加载测试计划模板 `.specify/templates/test-plan-template.md`

3. **执行测试计划工作流**：按照测试计划模板结构填充：

   ### 3.1 测试策略总览
   - 基于 feature 复杂度，确定 Integration 和 E2E 的投入比例
   - 定义本 feature 的分层边界（什么放 Integration、什么放 E2E）

   ### 3.2 各层测试详细计划
   - **Integration 测试**：根据 plan.md 的 API Contracts 和数据模型，列出集成路径验证内容、Mock 策略、测试数据隔离方案
   - **E2E 测试**：根据 spec.md 的 P1 User Story 和 Acceptance Scenarios，列出端到端路径和 Playwright 策略

   ### 3.3 测试基础设施
   - 列出所需的 fixture（DB 隔离、用户工厂、认证客户端）
   - 确定并行执行策略

   ### 3.4 覆盖率与验收
   - 根据宪章要求，填写本 feature 的具体覆盖率目标和门禁状态
   - 建立宪章要求的 data-testid 覆盖验证

   ### 3.5 测试与 Spec 可追溯性
   - 建立 FR → Test 映射表（每条 FR 必须有对应测试）
   - 建立 User Story → Test 映射表（每个 Story 必须有对应的独立验证方式）

   ### 3.6 测试风险与缓解
   - 识别本 feature 特有的测试风险（异步操作、外部依赖、状态管理等）

4. **停止并报告**：命令结束后，报告测试计划路径和生成的制品。

5. **检查扩展钩子**：检查 `.specify/extensions.yml` 中的 `hooks.after_test_plan` 键（格式同 before 钩子）。

## 关键规则

- 使用绝对路径进行文件系统操作；在文档中使用项目相对路径进行引用。
- 测试计划 MUST 与 spec.md 和 plan.md 保持一致，不得引入 spec 中未要求的功能测试。
- 每条 FR 必须有至少一个对应的测试用例（integration 或 E2E）。
- E2E 测试数量不得超过 User Story 的 Acceptance Scenario 数量加上关键边缘场景。
- 如果门禁检查中有 FAIL 项，必须在测试风险章节说明缓解措施。

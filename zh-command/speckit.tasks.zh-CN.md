---
description: 基于可用的设计工件，为功能生成可执行、按依赖排序的 tasks.md。
handoffs:
  - label: 一致性分析
    agent: speckit.analyze
    prompt: 对项目进行一致性分析
    send: true
  - label: 实施项目
    agent: speckit.implement
    prompt: 按阶段开始实施
    send: true
---

## 用户输入

```text
$ARGUMENTS
```

在继续之前，你**必须**考虑用户输入的内容（如果不为空）。

## 执行前检查

**检查扩展钩子（任务生成前）**：
- 检查项目根目录下是否存在 `.specify/extensions.yml`。
- 如果存在，读取它并查找 `hooks.before_tasks` 键下的条目。
- 如果 YAML 无法解析或无效，静默跳过钩子检查并正常继续。
- 过滤掉 `enabled` 明确为 `false` 的钩子。没有 `enabled` 字段的钩子默认视为已启用。
- 对于每个剩余的钩子，**不要**尝试解析或评估钩子的 `condition` 表达式：
  - 如果钩子没有 `condition` 字段，或者 `condition` 为 null/空，则视为该钩子可执行。
  - 如果钩子定义了非空的 `condition`，则跳过该钩子，条件评估留给 HookExecutor 实现处理。
- 对于每个可执行的钩子，根据其 `optional` 标志输出以下内容：
  - **可选钩子**（`optional: true`）：
    ```
    ## 扩展钩子

    **可选前置钩子**：{extension}
    命令：`/{command}`
    描述：{description}

    提示：{prompt}
    执行：`/{command}`
    ```
  - **强制钩子**（`optional: false`）：
    ```
    ## 扩展钩子

    **自动前置钩子**：{extension}
    正在执行：`/{command}`
    EXECUTE_COMMAND: {command}
    
    在继续大纲之前等待钩子命令的执行结果。
    ```
- 如果没有注册任何钩子，或 `.specify/extensions.yml` 不存在，则静默跳过。

## 大纲

1. **设置**：从仓库根目录运行 `.specify/scripts/bash/setup-tasks.sh --json` 并解析 `FEATURE_DIR`、`TASKS_TEMPLATE` 和 `AVAILABLE_DOCS` 列表。提供的 `FEATURE_DIR` 和 `TASKS_TEMPLATE` 必须是绝对路径。`AVAILABLE_DOCS` 是 `FEATURE_DIR` 下可用的文档名称/相对路径列表（例如 `research.md` 或 `contracts/`）。对于像 "I'm Groot" 这样的单引号参数，请使用转义语法：例如 `'I'\''m Groot'`（或使用双引号：`"I'm Groot"`）。

2. **加载设计文档**：从 `FEATURE_DIR` 读取：
   - **必需**：`plan.md`（技术栈、库、结构），`spec.md`（带优先级的用户故事）
   - **可选**：`data-model.md`（实体），`contracts/`（接口契约），`research.md`（决策），`quickstart.md`（测试场景）
   - 注意：并非所有项目都有所有文档。根据可用的内容生成任务。

3. **执行任务生成工作流**：
   - 加载 `plan.md` 并提取技术栈、库、项目结构
   - 加载 `spec.md` 并提取用户故事及其优先级（P1、P2、P3 等）
   - 如果 `data-model.md` 存在：提取实体并映射到用户故事
   - 如果 `contracts/` 存在：将接口契约映射到用户故事
   - 如果 `research.md` 存在：提取设置任务的决策
   - 按用户故事组织生成任务（参见下方的任务生成规则）
   - 生成显示用户故事完成顺序的依赖图
   - 为每个用户故事创建并行执行示例
   - 验证任务完整性（每个用户故事都有所有需要的任务，可独立测试）

4. **生成 tasks.md**：从 `TASKS_TEMPLATE`（来自上述 JSON 输出）读取任务模板并用作结构。如果 `TASKS_TEMPLATE` 为空，回退到 `.specify/templates/tasks-template.md`。填充：
   - 来自 `plan.md` 的正确的功能名称
   - 第 1 阶段：设置任务（项目初始化）
   - 第 2 阶段：基础任务（所有用户故事的阻塞前置条件）
   - 第 3 阶段及以后：每个用户故事一个阶段（按 `spec.md` 中的优先级顺序）
   - 每个阶段包括：故事目标、独立测试标准、测试（如请求）、实现任务
   - 最终阶段：完善与跨领域关注点
   - 所有任务必须遵循严格的检查清单格式（参见下方的任务生成规则）
   - 每个任务的清晰文件路径
   - 显示故事完成顺序的依赖关系部分
   - 每个故事的并行执行示例
   - 实施策略部分（优先 MVP，增量交付）

5. **报告**：输出生成的 `tasks.md` 路径和摘要：
   - 总任务数
   - 每个用户故事的任务数
   - 识别的并行机会
   - 每个故事的独立测试标准
   - 建议的 MVP 范围（通常只是用户故事 1）
   - 格式验证：确认**所有**任务遵循检查清单格式（复选框、ID、标签、文件路径）

6. **检查扩展钩子**：生成 `tasks.md` 后，检查项目根目录下是否存在 `.specify/extensions.yml`。
   - 如果存在，读取它并查找 `hooks.after_tasks` 键下的条目。
   - 如果 YAML 无法解析或无效，静默跳过钩子检查并正常继续。
   - 过滤掉 `enabled` 明确为 `false` 的钩子。没有 `enabled` 字段的钩子默认视为已启用。
   - 对于每个剩余的钩子，**不要**尝试解析或评估钩子的 `condition` 表达式：
     - 如果钩子没有 `condition` 字段，或者 `condition` 为 null/空，则视为该钩子可执行。
     - 如果钩子定义了非空的 `condition`，则跳过该钩子，条件评估留给 HookExecutor 实现处理。
   - 对于每个可执行的钩子，根据其 `optional` 标志输出以下内容：
     - **可选钩子**（`optional: true`）：
       ```
       ## 扩展钩子

       **可选钩子**：{extension}
       命令：`/{command}`
       描述：{description}

       提示：{prompt}
       执行：`/{command}`
       ```
     - **强制钩子**（`optional: false`）：
       ```
       ## 扩展钩子

       **自动钩子**：{extension}
       正在执行：`/{command}`
       EXECUTE_COMMAND: {command}
       ```
   - 如果没有注册任何钩子，或 `.specify/extensions.yml` 不存在，则静默跳过。

任务生成的上下文：$ARGUMENTS

`tasks.md` 应该是可立即执行的——每个任务必须足够具体，以至于 LLM 可以在没有额外上下文的情况下完成它。

## 任务生成规则

**关键**：任务**必须**按用户故事组织，以启用独立实现和测试。

**测试是可选的**：仅在功能规格中明确要求或用户请求 TDD 方法时才生成测试任务。

### 检查清单格式（必需）

每个任务必须严格遵循此格式：

```text
- [ ] [TaskID] [P?] [Story?] Description with file path
```

**格式组件**：

1. **复选框**：**始终**以 `- [ ]` 开头（markdown 复选框）
2. **任务 ID**：按执行顺序的连续编号（T001、T002、T003…）
3. **[P] 标记**：仅当任务可并行化时包含（不同文件，无对未完成任务的依赖）
4. **[Story] 标签**：**仅**用户故事阶段任务需要
   - 格式：[US1]、[US2]、[US3] 等（映射到 `spec.md` 中的用户故事）
   - 设置阶段：无故事标签
   - 基础阶段：无故事标签  
   - 用户故事阶段：**必须**有故事标签
   - 完善阶段：无故事标签
5. **描述**：清晰的操作和精确的文件路径

**示例**：

- ✅ 正确: `- [ ] T001 Create project structure per implementation plan`
- ✅ 正确: `- [ ] T005 [P] Implement authentication middleware in src/middleware/auth.py`
- ✅ 正确: `- [ ] T012 [P] [US1] Create User model in src/models/user.py`
- ✅ 正确: `- [ ] T014 [US1] Implement UserService in src/services/user_service.py`
- ❌ 错误: `- [ ] Create User model`（缺少 ID 和故事标签）
- ❌ 错误: `T001 [US1] Create model`（缺少复选框）
- ❌ 错误: `- [ ] [US1] Create User model`（缺少任务 ID）
- ❌ 错误: `- [ ] T001 [US1] Create model`（缺少文件路径）

### 任务组织

1. **来自用户故事（spec.md）** - 主要组织方式：
   - 每个用户故事（P1、P2、P3…）获得自己的阶段
   - 将所有相关组件映射到故事：
     - 故事所需的模型
     - 故事所需的服务
     - 故事所需的接口/UI
     - 如果请求测试：特定于该故事的测试
   - 标记故事依赖关系（大多数故事应该是独立的）

2. **来自契约**：
   - 将每个接口契约映射 → 到它服务的用户故事
   - 如果请求测试：每个接口契约 → 在该故事阶段实现之前的契约测试任务 [P]

3. **来自数据模型**：
   - 将每个实体映射到需要它的用户故事
   - 如果实体服务于多个故事：放入最早的故事或设置阶段
   - 关系 → 适当故事阶段的服务层任务

4. **来自设置/基础设施**：
   - 共享基础设施 → 设置阶段（第 1 阶段）
   - 基础/阻塞任务 → 基础阶段（第 2 阶段）
   - 特定故事的设置 → 在该故事的阶段内

### 阶段结构

- **第 1 阶段**：设置（项目初始化）
- **第 2 阶段**：基础（阻塞前置条件 - 必须在用户故事之前完成）
- **第 3 阶段及以后**：用户故事按优先级顺序（P1、P2、P3…）
  - 在每个故事内：测试（如请求）→ 模型 → 服务 → 端点 → 集成
  - 每个阶段应该是完整的、可独立测试的增量
- **最终阶段**：完善与跨领域关注点

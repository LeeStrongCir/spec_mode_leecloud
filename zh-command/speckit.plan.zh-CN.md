---
description: 使用规划模板执行实施计划工作流，生成设计工件。
handoffs:
  - label: 创建任务
    agent: speckit.tasks
    prompt: 将计划拆分为具体任务
    send: true
  - label: 创建检查清单
    agent: speckit.checklist
    prompt: 为以下领域创建检查清单...
    send: true
---

## 用户输入

```text
$ARGUMENTS
```

在继续之前，你**必须**考虑用户输入的内容（如果不为空）。

## 执行前检查

**检查扩展钩子（计划前）**：
- 检查项目根目录下是否存在 `.specify/extensions.yml`。
- 如果存在，读取它并查找 `hooks.before_plan` 键下的条目。
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

1. **设置**：从仓库根目录运行 `.specify/scripts/bash/setup-plan.sh --json` 并解析 JSON 获取 `FEATURE_SPEC`、`IMPL_PLAN`、`SPECS_DIR`、`BRANCH`。对于像 "I'm Groot" 这样的单引号参数，请使用转义语法：例如 `'I'\''m Groot'`（或使用双引号：`"I'm Groot"`）。

2. **加载上下文**：读取 `FEATURE_SPEC` 和 `.specify/memory/constitution.md`。加载 `IMPL_PLAN` 模板（已拷贝）。

3. **执行计划工作流**：按照 `IMPL_PLAN` 模板中的结构执行：
   - 填写技术上下文（将未知项标记为 "NEEDS CLARIFICATION"）
   - 根据宪章填写宪章检查部分
   - 评估门禁（如果违规行为未被合理解释则报错）
   - 第 0 阶段：生成 `research.md`（解决所有 NEEDS CLARIFICATION）
   - 第 1 阶段：生成 `data-model.md`、`contracts/`、`quickstart.md`
   - 第 1 阶段：通过运行代理脚本更新代理上下文
   - 在设计完成后重新评估宪章检查

4. **停止并报告**：命令在第 2 阶段计划后结束。报告分支、`IMPL_PLAN` 路径和生成的产物。

5. **检查扩展钩子**：报告完成后，检查项目根目录下是否存在 `.specify/extensions.yml`。
   - 如果存在，读取它并查找 `hooks.after_plan` 键下的条目。
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

## 阶段

### 第 0 阶段：大纲与研究

1. **从上述技术上下文中提取未知项**：
   - 对于每个 NEEDS CLARIFICATION → 研究任务
   - 对于每个依赖项 → 最佳实践任务
   - 对于每个集成点 → 模式任务

2. **生成并派发研究代理**：

   ```text
   对于技术上下文中的每个未知项：
     任务："为 {功能上下文} 研究 {未知项}"
   对于每个技术选型：
     任务："查找 {技术} 在 {领域} 中的最佳实践"
   ```

3. **在 `research.md` 中整合发现**，使用以下格式：
   - 决策：[选择了什么]
   - 理由：[为什么选择]
   - 考虑的替代方案：[还评估了哪些方案]

**输出**：`research.md`，所有 NEEDS CLARIFICATION 已解决。

### 第 1 阶段：设计与契约

**前置条件**：`research.md` 已完成。

1. **从功能规格中提取实体** → `data-model.md`：
   - 实体名称、字段、关系
   - 来自需求的验证规则
   - 状态转换（如果适用）

2. **定义接口契约**（如果项目有外部接口）→ `/contracts/`：
   - 确定项目向用户或其他系统暴露哪些接口
   - 记录适合该项目类型的契约格式
   - 示例：库的公共 API、CLI 工具的命令模式、Web 服务的端点、解析器的语法、应用程序的 UI 契约
   - 如果项目纯粹是内部使用的（构建脚本、一次性工具等），则跳过此步

3. **代理上下文更新**：
   - 更新 `AGENTS.md` 中 `<!-- SPECKIT START -->` 和 `<!-- SPECKIT END -->` 标记之间的计划引用，使其指向在第 1 步中创建的计划文件（`IMPL_PLAN` 路径）。

**输出**：`data-model.md`、`/contracts/*`、`quickstart.md`、已更新的代理上下文文件。

## 关键规则

- 使用绝对路径进行文件系统操作；在文档和代理上下文文件中使用项目相对路径进行引用。
- 如果门禁失败或有未解决的澄清项，则报错（ERROR）。

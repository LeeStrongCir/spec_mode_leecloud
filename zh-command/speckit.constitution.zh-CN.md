---
description: 根据交互式或提供的项目原则输入，创建或更新项目宪法，并确保所有依赖模板保持同步。
handoffs: 
  - label: 构建规范
    agent: speckit.specify
    prompt: 根据更新后的宪法实现功能规范。我想要构建...
---

## 用户输入

```text
$ARGUMENTS
```

你**必须**在继续之前考虑用户输入（如果不为空）。

## 执行前检查

**检查扩展钩子（在宪法更新之前）**：
- 检查项目根目录下是否存在 `.specify/extensions.yml`。
- 如果存在，读取它并查找 `hooks.before_constitution` 键下的条目
- 如果 YAML 无法解析或无效，静默跳过钩子检查并正常继续
- 过滤掉 `enabled` 显式为 `false` 的钩子。没有 `enabled` 字段的钩子默认视为启用。
- 对于每个剩余的钩子，**不要**尝试解释或评估钩子的 `condition` 表达式：
  - 如果钩子没有 `condition` 字段，或为空/null，则视为可执行
  - 如果钩子定义了非空的 `condition`，则跳过该钩子，将条件评估留给 HookExecutor 实现
- 对于每个可执行钩子，根据其 `optional` 标志输出以下内容：
  - **可选钩子**（`optional: true`）：
    ```
    ## 扩展钩子

    **可选前置钩子**：{extension}
    命令：`/{command}`
    描述：{description}

    提示词：{prompt}
    执行：`/{command}`
    ```
  - **强制钩子**（`optional: false`）：
    ```
    ## 扩展钩子

    **自动前置钩子**：{extension}
    正在执行：`/{command}`
    EXECUTE_COMMAND: {command}

    在执行下一步之前，等待钩子命令的结果。
    ```
- 如果没有注册钩子或 `.specify/extensions.yml` 不存在，则静默跳过

## 执行流程

你正在更新位于 `.specify/memory/constitution.md` 的项目宪法文件。该文件是一个包含方括号占位符标记（如 `[PROJECT_NAME]`、`[PRINCIPLE_1_NAME]`）的模板。你的任务是：(a) 收集/推导具体值，(b) 精确填充模板，(c) 将任何修正传播到依赖产物。

**注意**：如果 `.specify/memory/constitution.md` 尚不存在，它应该在项目设置期间从 `.specify/templates/constitution-template.md` 初始化。如果缺失，请先复制模板。

按照以下执行流程操作：

1. 加载现有的宪法文件 `.specify/memory/constitution.md`。
   - 识别所有形如 `[ALL_CAPS_IDENTIFIER]` 的占位符标记。
   **重要**：用户可能需要比模板中更少或更多的原则。如果指定了数量，请遵循该数量——遵循通用模板。

2. 收集/推导占位符的值：
   - 如果用户输入（对话）提供了值，请使用它。
   - 否则从现有仓库上下文中推断（README、文档、或嵌入的先前宪法版本）。
   - 关于治理日期：`RATIFICATION_DATE` 是原始采用日期（如果未知则询问或标记 TODO），`LAST_AMENDED_DATE` 如果进行了更改则为今天，否则保留之前的日期。
   - `CONSTITUTION_VERSION` 必须根据语义化版本规则递增：
     - MAJOR（主版本）：向后不兼容的治理/原则删除或重新定义。
     - MINOR（次版本）：新增原则/章节或实质性扩展指导。
     - PATCH（补丁版本）：澄清、措辞、拼写修正、非语义的改进。
   - 如果版本升级类型不明确，在最终确定前提出推理。

3. 草拟更新后的宪法内容：
   - 将所有占位符替换为具体文本（不留下括号标记，除非项目有意选择暂不定义的模板槽位——必须明确说明理由）。
   - 保持标题层级，注释在替换后可以移除，除非它们仍然提供澄清性指导。
   - 确保每个原则部分：简洁的名称行、段落（或项目符号列表）捕获不可协商的规则、若不明显则说明明确的基本原理。
   - 确保治理部分列出修改程序、版本控制策略和合规性审查期望。

4. 一致性传播检查清单（将先前的检查清单转化为主动验证）：
   - 读取 `.specify/templates/plan-template.md` 并确保任何"宪法检查"或规则与更新后的原则保持一致。
   - 读取 `.specify/templates/spec-template.md` 以检查范围/需求对齐——如果宪法新增或删除了强制性章节或约束，则进行更新。
   - 读取 `.specify/templates/tasks-template.md` 并确保任务分类反映了新增或删除的原则驱动的任务类型（如可观察性、版本控制、测试纪律）。
   - 读取 `.specify/templates/commands/*.md` 中的每个命令文件（包括本文件）以验证是否在需要通用指导时仍存在过时的引用（如仅限 CLAUDE 的代理特定名称）。
   - 读取任何运行时指导文档（如 `README.md`、`docs/quickstart.md` 或代理特定的指导文件）。更新对已更改原则的引用。

5. 生成同步影响报告（更新后作为 HTML 注释添加到宪法文件顶部）：
   - 版本变更：旧版本 → 新版本
   - 已修改的原则列表（如果重命名则显示旧标题 → 新标题）
   - 新增章节
   - 删除的章节
   - 需要更新的模板（✅ 已更新 / ⚠ 待处理）及文件路径
   - 如果有意延迟任何占位符，列出后续 TODO 项。

6. 最终输出前的验证：
   - 没有剩余的未解释的括号标记。
   - 版本行与报告一致。
   - 日期采用 ISO 格式 YYYY-MM-DD。
   - 原则是声明式的、可测试的，并且没有模糊语言（"should" → 在适当的情况下替换为 MUST/SHOULD 及其理由）。

7. 将完成的宪法写回 `.specify/memory/constitution.md`（覆盖写入）。

8. 向用户输出最终摘要，包括：
   - 新版本和升级理由。
   - 任何标记为需要手动跟进的文件。
   - 建议的提交消息（例如 `docs: amend constitution to vX.Y.Z (principle additions + governance update)`）。

格式与样式要求：

- 严格按照模板使用 Markdown 标题（不要降级/升级级别）。
- 换行长理由行以保持可读性（理想情况下 <100 字符），但不要强行用别扭的断行方式。
- 章节之间保持单个空行。
- 避免尾随空格。

如果用户提供部分更新（例如仅修订一个原则），仍需执行验证和版本决策步骤。

如果缺少关键信息（例如采用日期确实未知），插入 `TODO(<FIELD_NAME>): 解释说明` 并在同步影响报告的延迟项中列出。

不要创建新模板；始终在现有的 `.specify/memory/constitution.md` 文件上操作。

## 执行后检查

**检查扩展钩子（在宪法更新之后）**：
检查项目根目录下是否存在 `.specify/extensions.yml`。
- 如果存在，读取它并查找 `hooks.after_constitution` 键下的条目
- 如果 YAML 无法解析或无效，静默跳过钩子检查并正常继续
- 过滤掉 `enabled` 显式为 `false` 的钩子。没有 `enabled` 字段的钩子默认视为启用。
- 对于每个剩余的钩子，**不要**尝试解释或评估钩子的 `condition` 表达式：
  - 如果钩子没有 `condition` 字段，或为空/null，则视为可执行
  - 如果钩子定义了非空的 `condition`，则跳过该钩子，将条件评估留给 HookExecutor 实现
- 对于每个可执行钩子，根据其 `optional` 标志输出以下内容：
  - **可选钩子**（`optional: true`）：
    ```
    ## 扩展钩子

    **可选后置钩子**：{extension}
    命令：`/{command}`
    描述：{description}

    提示词：{prompt}
    执行：`/{command}`
    ```
  - **强制钩子**（`optional: false`）：
    ```
    ## 扩展钩子

    **自动后置钩子**：{extension}
    正在执行：`/{command}`
    EXECUTE_COMMAND: {command}
    ```
- 如果没有注册钩子或 `.specify/extensions.yml` 不存在，则静默跳过

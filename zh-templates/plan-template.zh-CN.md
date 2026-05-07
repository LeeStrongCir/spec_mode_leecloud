# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: 本模板由 `/speckit.plan` 命令填充。执行流程详见 `.specify/templates/plan-template.md`。

## Summary

[从 feature spec 中提取：primary requirement + research 中的 technical approach]

## Technical Context

<!--
  ACTION REQUIRED: 将本节内容替换为项目的具体技术细节。
  此处的结构仅供参考，用于指导迭代过程。
-->

**Language/Version**: [例如 Python 3.11, Swift 5.9, Rust 1.75 或 NEEDS CLARIFICATION]  
**Primary Dependencies**: [例如 FastAPI, UIKit, LLVM 或 NEEDS CLARIFICATION]  
**Storage**: [如适用，例如 PostgreSQL, CoreData, files 或 N/A]  
**Testing**: [例如 pytest, XCTest, cargo test 或 NEEDS CLARIFICATION]  
**Target Platform**: [例如 Linux server, iOS 15+, WASM 或 NEEDS CLARIFICATION]
**Project Type**: [例如 library/cli/web-service/mobile-app/compiler/desktop-app 或 NEEDS CLARIFICATION]  
**Performance Goals**: [领域相关，例如 1000 req/s, 10k lines/sec, 60 fps 或 NEEDS CLARIFICATION]  
**Constraints**: [领域相关，例如 <200ms p95, <100MB memory, offline-capable 或 NEEDS CLARIFICATION]  
**Scale/Scope**: [领域相关，例如 10k users, 1M LOC, 50 screens 或 NEEDS CLARIFICATION]

## Constitution Check

*GATE: 必须在 Phase 0 research 之前通过。Phase 1 design 之后需重新检查。*

[根据 constitution file 确定的 Gates]

## Project Structure

### Documentation (本 feature 相关)

```text
specs/[###-feature]/
├── plan.md              # 本文件 (/speckit.plan 命令输出)
├── research.md          # Phase 0 输出 (/speckit.plan 命令)
├── data-model.md        # Phase 1 输出 (/speckit.plan 命令)
├── quickstart.md        # Phase 1 输出 (/speckit.plan 命令)
├── contracts/           # Phase 1 输出 (/speckit.plan 命令)
└── tasks.md             # Phase 2 输出 (/speckit.tasks 命令 - 不由 /speckit.plan 创建)
```

### Source Code (仓库根目录)
<!--
  ACTION REQUIRED: 将下方的占位符树替换为本 feature 的具体结构。
  删除未使用的选项，并用真实路径扩展所选结构（例如 apps/admin, packages/something）。
  交付的 plan 中不能包含 Option 标签。
-->

```text
# [若未使用请删除] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [若未使用请删除] Option 2: Web application (检测到 "frontend" + "backend" 时使用)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [若未使用请删除] Option 3: Mobile + API (检测到 "iOS/Android" 时使用)
api/
└── [同上方 backend 结构]

ios/ 或 android/
└── [平台特定结构: feature modules, UI flows, platform tests]
```

**Structure Decision**: [记录所选结构，并引用上方捕获的真实目录]

## Complexity Tracking

> **仅在 Constitution Check 存在需要合理化的 violations 时填写**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [例如 第4个项目] | [当前需求] | [为何3个项目不够] |
| [例如 Repository pattern] | [具体问题] | [为何直接 DB 访问不够] |

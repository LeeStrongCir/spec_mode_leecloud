# Implementation Plan: LECS Host Management

**Branch**: `007-lecs-hosts` | **Date**: 2026-05-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/007-lecs-hosts/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Implement LECS Host (cloud server) management for the Lee Cloud Console. Users can discover the feature via console search, view a list of their hosts with status statistics, and create new hosts through a multi-section configuration page (billing mode, instance spec, OS image, public network access, purchase quantity). Backend provides REST APIs for listing, creating, and deleting LECS Host instances. Frontend uses Jinja2 SSR templates styled with the existing console.css, with all interactive components annotated with `data-testid` attributes per the project constitution.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI 0.115+, SQLAlchemy 2.0 (async), PyJWT 2.9+, argon2-cffi 23.1+, Jinja2, Pydantic 2.5+, pydantic-settings 2.5+, Alembic, aiosqlite (dev), asyncpg (prod)  
**Storage**: SQLite (`dev.db`) for development → PostgreSQL for production. Alembic for migrations.  
**Testing**: pytest + pytest-asyncio + pytest-cov (90% minimum coverage) + Playwright E2E  
**Target Platform**: Linux server (FastAPI ASGI) serving SSR HTML via Jinja2 + static CSS  
**Project Type**: SSR web application (Jinja2 templates + FastAPI backend, no SPA framework)  
**Performance Goals**: API responses < 500ms at P95, list page load < 2 seconds, search-to-navigate < 1 second  
**Constraints**: Jinja2 SSR only (no client-side JavaScript framework), custom CSS only (no external CSS libraries), all interactive components must include `data-testid`, JWT Cookie auth only, region initially fixed to "华北-北京四"  
**Scale/Scope**: Single-user quota of 200 hosts max, 100 per single creation request; bandwidth 1-2000 Mbps

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The project constitution (`.specify/memory/constitution.md`) mandates:

1. **data-testid mandatory gate**: All interactive components (buttons, inputs, selects, checkboxes, radio groups) in the LECS Host List page and Creation page MUST have `data-testid` attributes. The spec's SC-004 explicitly requires 100% coverage. → **PASS** — SC-004 and FR-020 explicitly enforce this.
2. **Selection priority gate**: `data-testid` > `aria-label` > `role`+`name` > other selectors. → **PASS** — All selectors will use `data-testid` (FR-020).
3. **Semantic naming gate**: `[功能模块]-[元素类型]` format, lowercase hyphen-separated. → **PASS** — The spec includes a detailed `data-testid` naming table (Section 3.2) with 40+ defined attributes.
4. **Validation states gate**: Form components must include validation state identifiers. → **PASS** — Creation page has form validation (quota, bandwidth, billing mode rules) with error state display (FR-021, FR-022, FR-023).
5. **Loading/Error states gate**: Async components must include loading and result state identifiers. → **PASS** — Both list and create pages have explicit loading/success/failed/empty state requirements (Section 3.3 of spec).
6. **Quality gate**: 100% data-testid coverage for interactive components. → **PASS** — Enforced by SC-004 and the PR code review requirements in the constitution's workflow section.

**Result**: All gates PASS. No violations to justify.

## Project Structure

### Documentation (this feature)

```text
specs/007-lecs-hosts/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── src/app/
│   ├── models/
│   │   ├── lecs_host.py         # LECSHost SQLAlchemy model + LechsHostStatus enum + LechsBillingMode enum
│   │   └── instance_type.py     # InstanceType + InstanceSpec models (static config)
│   ├── schemas/
│   │   └── lecs_host.py         # Pydantic request/response schemas
│   ├── services/
│   │   └── lecs_host_service.py # Business logic: list_hosts(), create_host(), delete_host(), validate_quota()
│   ├── api/
│   │   ├── lecs_host.py         # REST endpoints: GET/POST /api/v1/lecs-hosts, DELETE /api/v1/lecs-hosts/{id}
│   │   └── deps.py              # (existing) auth dependencies reused
│   └── main.py                  # (modified) register lecs_host router
├── frontend/
│   ├── templates/
│   │   ├── lecs_host_list.html  # LECS Host List page (Jinja2)
│   │   └── lecs_host_create.html # LECS Host Creation page (Jinja2)
│   └── static/
│       └── css/
│           └── console.css      # (modified) add LECS Host specific styles
└── tests/
    ├── unit/
    │   └── test_lecs_host_service.py    # Unit tests for LechsService
    ├── integration/
    │   └── test_lecs_host_api.py        # API integration tests
    └── e2e/
        └── test_lecs_host_list.py       # Playwright E2E tests
```

**Structure Decision**: This follows the existing project architecture exactly — new model under `backend/src/app/models/`, new service under `backend/src/app/services/`, new API router under `backend/src/app/api/`, new Jinja2 templates under `backend/frontend/templates/`. SSR pattern is reused with `require_auth` dependency. The existing `console.css` is extended with LECS-specific styles rather than creating a new CSS file to minimize asset count.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitution violations. Complexity is within existing architectural patterns.

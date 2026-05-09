# Implementation Plan: Console Dashboard

**Branch**: `006-console-page-with-auth` | **Date**: 2026-05-07 | **Spec**: [specs/006-console-page-with-auth/spec.md](spec.md)
**Input**: Feature specification from `/specs/006-console-page-with-auth/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Build a read-only console dashboard page matching the Huawei Cloud console layout, rebranded as "Lee云". Create a new GET `/console` route with a Jinja2 template, protected by existing JWT authentication middleware. Seed a default admin user (admin/admin@123) via a database migration. Update the login redirect to `/console` after successful authentication. Replace all "华为云/HUAWEI CLOUD" text references with "Lee云/LEE CLOUD" across templates and CSS.

## Technical Context

**Language/Version**: Python 3.11, HTML/CSS/JS (Jinja2 SSR templates)  
**Primary Dependencies**: FastAPI 0.115+, SQLAlchemy 2.0 (async), Jinja2, Argon2id password hashing, JWT httpOnly cookies  
**Storage**: SQLite (development) → PostgreSQL (production)  
**Testing**: pytest with pytest-asyncio, coverage  
**Target Platform**: Linux server, web browser  
**Project Type**: Web application (SSR via Jinja2 + FastAPI, no frontend framework)  
**Performance Goals**: Page load < 2 seconds for login → console redirect; console dashboard render < 1 second  
**Constraints**: SSR-only (no SPA/framework), httpOnly cookie based auth, no external CSS libraries/CDNs for styling  
**Scale/Scope**: Single admin user initially; dashboard is read-only static data (mock data for v1)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Gate Evaluation Against Constitution v1.0.0

| Gate | Status | Justification |
|------|--------|---------------|
| Test-First (TDD) | **N/A (Optional)** | Console dashboard is "SSR UI Chrome" — per Constitution Section I, TDD is optional for "单季度内即可重构的 UI Chrome" |
| UI Component Coverage 60-70% | **PASS** | UI rendering test will cover the console template structure (6 sections verified) |
| Unit Test on Business Logic | **PASS** | Admin seeding logic will have unit test via factory pattern |
| Integration Test on Auth Flow | **PASS** | Login → redirect to console will be covered by existing integration test patterns |
| E2E Critical Path | **PASS** | Login with admin credential → reach console will constitute E2E critical path test |
| Accessibility (WCAG 2.2 AA) | **PASS** | HTML template uses semantic elements, ARIA roles, proper label associations |
| Security (OWASP Top 10) | **PASS** | Reuses existing JWT httpOnly cookie auth; dashboard is read-only with no data mutation; console route is protected |
| Performance (p95 within 5% baseline) | **PASS** | Static SSR rendering — no DB queries beyond auth check — inherently fast |
| No Critical/High security gaps | **PASS** | Admin password must be hashed with Argon2id (existing pattern); no PII exposed |
| No implementation-specific in spec | **PASS** | Spec is technology-agnostic; this plan handles the HOW |

**Gate Status**: ALL GATES PASS — proceeding to Phase 0 research.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
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
│   ├── main.py              # FastAPI entry + StaticFiles + console GET /console route
│   ├── config.py            # Pydantic Settings
│   ├── db.py                # Async engine + session factory
│   ├── models/
│   │   ├── user.py          # User model (add role field if not present)
│   │   ├── session.py
│   │   └── login_record.py
│   ├── schemas/
│   ├── services/
│   │   ├── auth.py          # Add admin seed function + session validation
│   │   ├── password.py
│   │   └── login_record.py
│   ├── api/
│   │   ├── auth.py          # Modify login redirect → /console
│   │   ├── login_record.py
│   │   └── deps.py          # Add require_auth dependency (redirect to /login)
│   ├── security/
│   └── middleware/
├── tests/
│   ├── test_console_auth.py      # Auth redirect integration tests
│   ├── test_seed_admin.py        # Admin seeding unit test
│   └── test_console_template.py  # Template rendering tests
├── alembic/
│   └── versions/                 # Add seed admin migration
└── frontend/
    ├── templates/
    │   ├── login.html            # Rebrand 华为云 → Lee云
    │   ├── login_history.html    # Rebrand 华为云 → Lee云
    │   ├── console.html          # NEW: Console dashboard page
    │   └── admin/
    │       └── login_records.html # Rebrand 华为云 → Lee云
    ├── static/
    │   ├── css/
    │   │   ├── style.css         # Console page styles + Lee Cloud token update
    │   │   └── console.css       # NEW: Console dashboard styles
    │   ├── js/
    │   └── fonts/                # Noto Sans SC woff2 files
```

**Structure Decision**: Single-project web application (backend only, since frontend is SSR via Jinja2 templates within backend). The console feature adds:
- One new route: `GET /console` in `src/app/main.py`
- One new template: `frontend/templates/console.html`
- One new CSS file: `frontend/static/css/console.css`
- One new dependency in `src/app/api/deps.py` for auth guard
- Admin seeding in existing `services/auth.py`
- Rebranding across all existing templates and `style.css`
- Login redirect modification in `api/auth.py`

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | No constitution violations |

---

## Constitution Check (Post-Design Re-evaluation)

After Phase 1 design completion, re-validated against Constitution v1.0.0:

| Gate | Status | Notes |
|------|--------|------|
| TDD Optional for UI Chrome | **PASS** | Dashboard is SSR UI template, TDD not required |
| Unit Tests for business logic | **PASS** | Admin seeding tested via `test_seed_admin.py`; Auth redirect tested via `test_console_auth.py` |
| Integration Tests for contracts | **PASS** | Login→console redirect flow tested as integration test |
| UI Coverage 60%+ | **PASS** | Template rendering tests verify 6 major sections render correctly |
| E2E Critical Path | **PASS** | Admin login → console dashboard = single E2E test |
| Accessibility (WCAG 2.2 AA) | **PASS** | HTML uses semantic tags, ARIA roles, proper form labels, focus management |
| Security (OWASP Top 10) | **PASS** | Reuses existing JWT/httpOnly auth; admin seeding uses runtime hashing (no hardcoded hash); password complexity met (admin@123) |
| Performance (p95 within 5%) | **PASS** | SSR rendering, no DB queries on console route beyond auth check |
| No critical/high security gaps | **PASS** | Admin seed uses existing `hash_password()` (Argon2id); username uniqueness enforced by existing UniqueIndex |
| Test code = Production code | **PASS** | Tests follow existing project patterns (pytest-asyncio, AAA structure) |

**Gate Status**: ALL GATES PASS — plan ready for task generation (`/speckit.tasks`).

</content>
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |

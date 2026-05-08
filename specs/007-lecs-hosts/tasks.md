# Tasks: LECS Hosts Management

**Input**: Design documents from `/specs/007-lecs-hosts/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api.md

**Tests**: Included — the spec mandates 100% `data-testid` coverage (constitution) and acceptance criteria for all user stories.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `backend/frontend/`, `backend/tests/`, `backend/alembic/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Alembic migration for new table.

- [ ] T001 Create Alembic migration for `lecs_hosts` table in `backend/alembic/versions/<timestamp>_add_lecs_hosts.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core models, schemas, validation, and async lifecycle infrastructure. All user stories depend on this phase.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T002 [P] Create `HostStatus` enum in `backend/src/app/models/lecs_host.py`
- [ ] T003 [P] Create `LECSHost` SQLAlchemy model with all fields per data-model.md in `backend/src/app/models/lecs_host.py`
- [ ] T004 [P] Update `backend/src/app/models/__init__.py` to export `HostStatus`, `LECSHost`
- [ ] T005 [P] Create Pydantic request/response schemas (CreateHostRequest, HostListItem, HostDetail, PaginatedHostList, ErrorResponse) in `backend/src/app/schemas/lecs_host.py`
- [ ] T006 [P] Create `INSTANCE_SPECS` constant dict with all 8 spec definitions in `backend/src/app/schemas/lecs_host.py`
- [ ] T007 Create validation helpers (hostname, username, password, IP, mask, duration) in `backend/src/app/utils/validators.py`
- [ ] T008 Create `LECSHostService` with CRUD methods (list, get_by_id, create, check_quota, count_user_hosts) in `backend/src/app/services/lecs_host_service.py`
- [ ] T009 Create `LECSLifecycleService` with `asyncio.create_task()` background workers for create (~30s), shutdown/start (~10s), delete (~5s) in `backend/src/app/services/lecs_lifecycle_service.py`
- [ ] T010 Create state machine transition matrix (dict mapping state → allowed operations) in `backend/src/app/services/lecs_lifecycle_service.py`
- [ ] T011 Register LECS host router and page routes in `backend/src/app/main.py` (include `/api/v1/lecs-hosts` prefix, `/console/lecs-hosts/list`, `/console/lecs-hosts/create`)
- [ ] T012 Add lifespan startup handler to reset stuck transitional hosts (creating/shutting_down/starting/deleting) on server restart in `backend/src/app/main.py`

**Checkpoint**: Foundation ready — user story implementation can now begin.

---

## Phase 3: User Story 1 — Search & Navigate to LECS Hosts List (Priority: P1) 🎯 MVP

**Goal**: User can search "LECS主机" in console search bar and navigate to the list page.

**Independent Test**: Search for "LECS" or "云服" in the console search bar; verify "LECS主机" appears with highlighted keywords; click to confirm navigation to `/console/lecs-hosts/list`; verify page loads (even if empty).

### Tests for User Story 1

- [ ] T013 [P] [US1] API test: GET `/api/v1/lecs-hosts` returns empty list for new user in `backend/tests/test_lecs_host_api.py`
- [ ] T014 [P] [US1] API test: GET `/api/v1/lecs-hosts` returns 401 without auth token in `backend/tests/test_lecs_host_api.py`

### Implementation for User Story 1

- [ ] T015 [P] [US1] Add "LECS主机" entry with `url: '/console/lecs-hosts/list'` to `serviceCatalog` in `backend/frontend/templates/console.html` and `backend/frontend/templates/console-full.html`
- [ ] T016 [US1] Implement `GET /api/v1/lecs-hosts` endpoint (paginated list, soft-delete filter, user-scoped, admin sees all) in `backend/src/app/api/lecs_host.py`
- [ ] T017 [US1] Create SSR list page template with table structure, "创建ECS主机" button, and `data-testid` attributes in `backend/frontend/templates/lecs_host_list.html`
- [ ] T018 [US1] Create list page CSS styles (data table, status badges, action buttons, disabled states) in `backend/frontend/static/css/lecs-host-list.css`
- [ ] T019 [US1] Create JavaScript module (list polling, state machine for button enable/disable, row rendering) in `backend/frontend/static/js/lecs-hosts.js`

**Checkpoint**: At this point, US1 should be fully functional — search reveals entry, click navigates to list, list loads (even empty).

---

## Phase 4: User Story 2 — View LECS Hosts List with Action Matrix (Priority: P1)

**Goal**: List page renders host data with state-machine-driven action buttons (shutdown/start/delete) that are correctly enabled or disabled per host status. Soft-deleted hosts are hidden.

**Independent Test**: Seed hosts in various states (normal, creating, stopped, failed, deleting); verify table renders all visible hosts; verify each row's action buttons match the state machine matrix; delete a host and confirm it disappears from the list.

### Tests for User Story 2

- [ ] T020 [P] [US2] API integration test: list with pagination, soft-delete filter in `backend/tests/test_lecs_host_api.py`
- [ ] T021 [US2] Service test: `check_quota` returns true at 99 hosts, false at 100 in `backend/tests/test_lecs_host_service.py`
- [ ] T022 [US2] Service test: `count_user_hosts` excludes soft-deleted records in `backend/tests/test_lecs_host_service.py`

### Implementation for User Story 2

- [ ] T023 [P] [US2] Create `_lecs_host_row.html` partial template with status badge rendering and action buttons with `data-testid` in `backend/frontend/templates/components/_lecs_host_row.html`
- [ ] T024 [US2] Implement frontend state machine JS object mapping status → {canShutdown, canStart, canDelete} in `backend/frontend/static/js/lecs-hosts.js`
- [ ] T025 [US2] Implement status polling (setInterval 3s when transitional states exist, auto-stop when all terminal) in `backend/frontend/static/js/lecs-hosts.js`
- [ ] T026 [US2] Implement button disabled logic (.disabled CSS class + disabled attribute based on state machine) in `backend/frontend/static/js/lecs-hosts.js`
- [ ] T027 [US2] Update list page template to render hosts from API response, integrate row partial, add pagination UI in `backend/frontend/templates/lecs_host_list.html`
- [ ] T028 [US2] Add admin host visibility (admin sees all users' hosts) to list endpoint in `backend/src/app/api/lecs_host.py`

**Checkpoint**: At this point, US1 + US2 both work — search → list → state-aware action buttons.

---

## Phase 5: User Story 3 — Create a LECS Host (Priority: P2)

**Goal**: Multi-step creation page with six configuration sections, real-time validation, cost calculation, confirmation dialog, and async submission.

**Independent Test**: Navigate from list page to creation page; fill all six sections; verify real-time validation errors on invalid input; verify cost display updates on spec/duration change; submit and see confirmation dialog; confirm and verify redirect to list with "创建中" status.

### Tests for User Story 3

- [ ] T029 [P] [US3] API contract test: POST `/api/v1/lecs-hosts` returns 201 with valid body in `backend/tests/test_lecs_host_api.py`
- [ ] T030 [P] [US3] API contract test: POST `/api/v1/lecs-hosts` returns 422 for invalid hostname in `backend/tests/test_lecs_host_api.py`
- [ ] T031 [P] [US3] API contract test: POST `/api/v1/lecs-hosts` returns 403 when quota exceeded in `backend/tests/test_lecs_host_api.py`
- [ ] T032 [US3] Validation test: hostname, username, password, IP, mask, duration helpers in `backend/tests/test_validators.py`

### Implementation for User Story 3

- [ ] T033 [P] [US3] Create `GET /api/v1/lecs-hosts/pricing` endpoint returning instance spec data in `backend/src/app/api/lecs_host.py`
- [ ] T034 [US3] Implement creation page template with six sections (basic config, instance, OS, IP, duration, cost) and `data-testid` attributes in `backend/frontend/templates/lecs_host_create.html`
- [ ] T035 [US3] Create creation page CSS styles (form layout, error messages, cards, price display) in `backend/frontend/static/css/lecs-host-create.css`
- [ ] T036 [US3] Implement client-side validation (hostname regex, credential complexity, IP format, mask range) with real-time red-text errors in `backend/frontend/static/js/lecs-hosts.js`
- [ ] T037 [US3] Implement cost calculation (subscription: price × months, on-demand: price ÷ 30) triggered on spec/billing/duration change in `backend/frontend/static/js/lecs-hosts.js`
- [ ] T038 [US3] Implement confirmation dialog (summary of all choices, total cost, "取消" / "确定" buttons, `data-testid`) in `backend/frontend/static/js/lecs-hosts.js`
- [ ] T039 [US3] Implement async create flow (submit → API → on success: redirect to list showing "创建中") in `backend/frontend/static/js/lecs-hosts.js`
- [ ] T040 [US3] Implement `POST /api/v1/lecs-hosts` endpoint with body validation, quota check, DB write, background task spawn, and 201 response in `backend/src/app/api/lecs_host.py`
- [ ] T041 [US3] Implement password hashing (reuse `hash_password` from `password_service`) and salted storage for LECS host credentials in `backend/src/app/services/lecs_host_service.py`
- [ ] T042 [US3] Create async create worker (sets status to `creating`, simulates 30s provisioning, transitions to `normal` or `failed` on timeout) in `backend/src/app/services/lecs_lifecycle_service.py`

**Checkpoint**: US1 + US2 + US3 all work — search → list → create host → async creation → list shows "创建中" → transitions to "正常".

---

## Phase 6: User Story 4 — Control Host Lifecycle (Shutdown/Start) (Priority: P3)

**Goal**: Shutdown and Start buttons work with async state transitions, respecting the state machine matrix.

**Independent Test**: With a "正常" host, click shutdown → status becomes "关机中" → ~10s later becomes "已关机" → "启动" button becomes available. With a "已关机" host, click start → status becomes "启动中" → ~10s later becomes "正常". During transitions, all buttons disabled.

### Tests for User Story 4

- [ ] T043 [P] [US4] API contract test: POST `/api/v1/lecs-hosts/{id}/shutdown` returns 200 for normal host in `backend/tests/test_lecs_host_api.py`
- [ ] T044 [P] [US4] API contract test: POST `/api/v1/lecs-hosts/{id}/shutdown` returns 409 for non-normal host in `backend/tests/test_lecs_host_api.py`
- [ ] T045 [P] [US4] API contract test: POST `/api/v1/lecs-hosts/{id}/start` returns 200 for stopped/failed host in `backend/tests/test_lecs_host_api.py`
- [ ] T046 [P] [US4] API contract test: POST `/api/v1/lecs-hosts/{id}/start` returns 409 for non-stopped/non-failed host in `backend/tests/test_lecs_host_api.py`
- [ ] T047 [US4] Lifecycle test: async shutdown task transitions creating → shutting_down → stopped in `backend/tests/test_lecs_lifecycle.py`
- [ ] T048 [US4] Lifecycle test: async start task transitions stopped → starting → normal in `backend/tests/test_lecs_lifecycle.py`

### Implementation for User Story 4

- [ ] T049 [US4] Implement `POST /api/v1/lecs-hosts/{id}/shutdown` endpoint (state guard → set `shutting_down` → spawn async task → 200 response) in `backend/src/app/api/lecs_host.py`
- [ ] T050 [US4] Implement `POST /api/v1/lecs-hosts/{id}/start` endpoint (state guard → set `starting` → spawn async task → 200 response) in `backend/src/app/api/lecs_host.py`
- [ ] T051 [US4] Implement async shutdown worker (10s sleep → set `stopped`) in `backend/src/app/services/lecs_lifecycle_service.py`
- [ ] T052 [US4] Implement async start worker (10s sleep → set `normal`) in `backend/src/app/services/lecs_lifecycle_service.py`
- [ ] T053 [US4] Wire lifecycle buttons in frontend JS (shutdown/start click handlers → API calls → optimistic UI update) in `backend/frontend/static/js/lecs-hosts.js`

**Checkpoint**: US1–US4 all work — full lifecycle: create → normal → shutdown → stopped → start → normal.

---

## Phase 7: User Story 5 — Safely Delete a Host (Priority: P4)

**Goal**: Delete with strict state restrictions, async soft-delete flow, and list removal.

**Independent Test**: Attempt delete on "正常" host → button disabled/interception. On "已关机" host → click delete → confirmation dialog → status becomes "删除中" → ~5s later row disappears from list, quota decreases.

### Tests for User Story 5

- [ ] T054 [P] [US5] API contract test: DELETE `/api/v1/lecs-hosts/{id}` returns 202 for stopped host in `backend/tests/test_lecs_host_api.py`
- [ ] T055 [P] [US5] API contract test: DELETE `/api/v1/lecs-hosts/{id}` returns 403 for normal host in `backend/tests/test_lecs_host_api.py`
- [ ] T056 [US5] Lifecycle test: async delete task sets `deleting` → `deleted_at` → removed from list query in `backend/tests/test_lecs_lifecycle.py`

### Implementation for User Story 5

- [ ] T057 [US5] Implement `DELETE /api/v1/lecs-hosts/{id}` endpoint (state guard: stopped/failed only → set `deleting` → spawn async task → 202 response) in `backend/src/app/api/lecs_host.py`
- [ ] T058 [US5] Implement async delete worker (~5s sleep → set `deleted_at`, clear status to `deleted`) in `backend/src/app/services/lecs_lifecycle_service.py`
- [ ] T059 [US5] Implement frontend delete confirmation dialog + click handler in `backend/frontend/templates/lecs_host_list.html` and `backend/frontend/static/js/lecs-hosts.js`
- [ ] T060 [US5] Implement frontend delete flow (confirm → API → row removed from DOM after backend confirms `deleted`) in `backend/frontend/static/js/lecs-hosts.js`

**Checkpoint**: All 5 user stories are independently functional — full lifecycle including deletion.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories.

- [ ] T061 [P] Add operation logging for all host lifecycle actions (create, delete, start, shutdown) including user, timestamp, IP, action in `backend/src/app/services/lecs_lifecycle_service.py`
- [ ] T062 [P] Create Playwright E2E test: full creation flow (fill form → submit → verify "创建中" → wait → verify "正常") in `backend/tests/test_lecs_host_e2e.py`
- [ ] T063 [P] Create Playwright E2E test: shutdown → stopped → start → normal flow in `backend/tests/test_lecs_host_e2e.py`
- [ ] T064 [P] Create Playwright E2E test: delete stopped host → verify row disappears in `backend/tests/test_lecs_host_e2e.py`
- [ ] T065 [P] Verify all `data-testid` attributes are present on interactive elements across both pages per constitution
- [ ] T066 Run `ruff check` and fix all lint errors in `backend/src/app/`
- [ ] T067 Run full test suite: `pytest tests/test_lecs_host* tests/test_validators.py tests/test_lecs_lifecycle.py -v --cov=src/app --cov-report=html`
- [ ] T068 Run quickstart.md validation checklist

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — **BLOCKS all user stories**
- **User Stories (Phase 3–7)**: All depend on Foundational phase completion
  - User stories can proceed sequentially in priority order (P1 → P2 → P3 → P4 → P4)
  - Or in parallel if multiple developers available
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **US1 (P1)**: After Foundational — delivers search + list page + GET API. No dependencies on other stories.
- **US2 (P1)**: After Foundational — depends on list API (US1) for data rendering. Can be combined with US1.
- **US3 (P2)**: After Foundational — standalone creation flow. Integrates with US1 (redirect to list).
- **US4 (P3)**: After Foundational — depends on model + lifecycle service (Phase 2). Integrates with US2 (list page buttons).
- **US5 (P4)**: After Foundational — depends on model + lifecycle service (Phase 2). Integrates with US2 (list page buttons).

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- T002–T006 [P] can run in parallel (4 new files, no cross-dependencies)
- T013–T014 [P] can run in parallel (different test functions, same file — serialize)
- T015 [P] + T016 [P] can run in parallel (template + API, different files)
- T017 + T018 [P] can run in parallel (HTML template + CSS file)
- T020–T022 [P] can run in parallel (different test files/functions)
- T029–T031 [P] can run in parallel (3 API contract tests)
- T033 [P] + T034 [P] + T035 [P] can run in parallel (different files)
- T043–T046 [P] can run in parallel (4 API contract tests)
- T054–T055 [P] can run in parallel (2 API contract tests)
- T061–T065 [P] can run in parallel (5 tasks, different files)

---

## Parallel Example: Foundational Phase

```bash
# Launch all parallel foundational tasks together:
# T002: HostStatus enum in models/lecs_host.py
# T003: LECSHost model in models/lecs_host.py  (extends T002 output — wait for T002)
# T005: Pydantic schemas in schemas/lecs_host.py
# T006: INSTANCE_SPECS constant in schemas/lecs_host.py

# Correct parallel group (no cross-file deps):
# Group A: models/lecs_host.py (T002 + T003 sequential — same file)
# Group B: schemas/lecs_host.py (T005 + T006 sequential — same file)
# Group A and B can run in parallel
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 2: Foundational (T002–T012)
3. Complete Phase 3: US1 (T013–T019) — search + list page + GET API
4. Complete Phase 4: US2 (T020–T028) — action matrix + polling
5. **STOP and VALIDATE**: Search → list → state-aware buttons all work

### Incremental Delivery

1. Setup + Foundational → migration + models + services ready
2. Add US1 + US2 → List page with action matrix (MVP!)
3. Add US3 → Host creation flow
4. Add US4 → Shutdown / Start lifecycle control
5. Add US5 → Delete with state restrictions
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:
1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: US1 + US2 (list + action matrix)
   - Developer B: US3 (creation page)
   - Developer C: US4 + US5 (lifecycle + delete)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- **Total task count**: 68
- **Task distribution**: Setup (1) + Foundational (11) + US1 (7) + US2 (9) + US3 (10) + US4 (10) + US5 (7) + Polish (8) + Tests (5 in-contract)
- **Parallel opportunities**: 15 groups identified

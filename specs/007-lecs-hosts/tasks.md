---

description: "Task list for implementing LECS Host Management (cloud server creation, listing, deletion)"
---

# Tasks: LECS Host Management

**Input**: Design documents from `/specs/007-lecs-hosts/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`

**Tests**: Tests are INCLUDED — the project constitution requires 90% minimum coverage. Each service and API endpoint must have corresponding unit/integration tests.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `backend/tests/`, `backend/frontend/`
- All paths relative to project root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure (Already done)

*No setup tasks required. Project structure, dependencies (FastAPI, SQLAlchemy, Jinja2, PyJWT, argon2-cffi), and base infrastructure from spec 006 are already in place.*

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T001 [P] [US2] Add `LechsHostStatus` and `LechsBillingMode` enums in `backend/src/app/models/lecs_host.py`
- [ ] T002 [US2] Create `LECSHost` SQLAlchemy model with all 21 fields (id, user_id, name, status, region, billing_mode, duration, expire_at, instance_type_id, os_image_id, enable_public_ip, bandwidth_billing_mode, bandwidth_mbps, public_ip, private_ip, enable_security, auto_renew, quantity, price_amount, timestamps, deleted_at) + `ix_lecs_hosts_user_id`, `ix_lecs_hosts_region`, `ix_lecs_hosts_status`, `ix_lecs_hosts_deleted_at` indexes in `backend/src/app/models/lecs_host.py`
- [ ] T003 [P] [US3] Create `InstanceType` SQLAlchemy model (name PK, category, description) in `backend/src/app/models/instance_type.py`
- [ ] T004 [P] [US3] Create `InstanceSpec` SQLAlchemy model (id PK, instance_type_id FK, vcpus, memory_gib, system_disk_type, system_disk_gib, monthly_price, is_available) in `backend/src/app/models/instance_type.py`
- [ ] T005 [P] [US3] Create `OSImage` SQLAlchemy model (name PK, family, version, arch, default_disk_gib, is_available, sort_order) in `backend/src/app/models/instance_type.py`
- [ ] T006 Create Alembic migration for 4 new tables (`lecs_hosts`, `instance_types`, `instance_specs`, `os_images`) in `backend/alembic/versions/` via `alembic revision --autogenerate -m "add lecs host tables"` and verify generated migration
- [ ] T007 Add `lifespan` seed function to populate `instance_types`, `instance_specs`, `os_images` tables with initial data (3 instance types: economy/x1, high_cost_performance/s3, high_performance/c7; at least 4 InstanceSpec records; 13 OS images including Huawei Cloud EulerOS as first) in `backend/src/app/main.py`
- [ ] T008 [P] [US2] Create `LecsHostListResponse`, `LecsHostCreateRequest`, `LecsHostCreateResponse`, `LecsHostDeleteResponse` Pydantic schemas in `backend/src/app/schemas/lecs_host.py`
- [ ] T009 [P] [US3] Create `InstanceTypeCatalogResponse`, `OSImageListResponse` Pydantic schemas in `backend/src/app/schemas/lecs_host.py`

**Checkpoint**: Foundation ready — all 4 models exist, migration is ready to run, seed data is defined, schemas are in place.

---

## Phase 3: User Story 1 — Search & Navigate to LECS Host List (Priority: P1) 🎯

**Goal**: Logged-in users can type "LECS主机" or "云服务器" in the console search bar, see "LECS主机" in the results, and click to navigate to `/console/lecs-hosts/list`.

**Independent Test**: Log in, enter "LECS主机" in the console search bar, verify "LECS主机" appears in results with highlighting, click it, verify browser navigates to `/console/lecs-hosts/list`. Also test "云服务器" synonym match. Unauthenticated users attempting direct URL access are redirected to `/login`.

### Implementation for User Story 1

- [ ] T010 [US1] Add `GET /console/lecs-hosts/list` route handler (HTMLResponse) protected by `require_auth`, returning `lecs_host_list.html` template with context `{"user": user, "page": "lecs_hosts"}` in `backend/src/app/main.py`
- [ ] T011 [US1] Create `lecs_host_list.html` Jinja2 template with page header ("LECS主机" tab), top navigation (reuse existing console nav), breadcrumbs, and a minimal placeholder body in `backend/frontend/templates/lecs_host_list.html`
- [ ] T012 [US1] Add "LECS主机" search result entry to the existing console search data structure (inline JS or template variable) so that "LECS主机" and "云服务器" keywords match, with link to `/console/lecs-hosts/list` in `backend/frontend/templates/console.html`

**Checkpoint**: At this point, User Story 1 is fully functional. Users can search for "LECS主机" from any console page and navigate to the dedicated list page. The list page renders with the standard console layout. (Actual host data display comes in US2.)

---

## Phase 4: User Story 2 — View LECS Host List with Status Dashboard (Priority: P1) 🎯

**Goal**: Authenticated users viewing `/console/lecs-hosts/list` see the status dashboard (5 statistics: 监控告警, 安全风险, 待续费, 未安装UniAgent, 配置提醒), action toolbar (开机, 关机, 重启, 重置密码, 续费, 更多, 导出), a search/filter bar ("默认按照名称搜索、过滤"), and a data table with columns (名称/ID, 监控, 安全, 状态, 规格/镜像, IP地址, 计费模式, 标签, 操作). When no hosts exist, an empty state with "购买弹性云服务器" button and region selector is shown.

**Independent Test**: With 0 hosts, list page shows empty state with purchase button. Create hosts via direct DB insert or API, then reload page — hosts appear in data table with correct columns. Test pagination by creating >20 hosts. Test search filter by host name.

### Tests for User Story 2 ⚠️

- [ ] T013 [US2] Write unit test for `list_hosts()` service method covering pagination, region filter, status filter, name search in `backend/tests/unit/test_lecs_host_service.py`
- [ ] T014 [US2] Write unit test for `delete_host()` service method covering happy path, not-found, and wrong-user in `backend/tests/unit/test_lecs_host_service.py`
- [ ] T015 [US2] Write unit test for `validate_quota()` covering quota exceeded and single-request limit (100) in `backend/tests/unit/test_lecs_host_service.py`
- [ ] T016 [US2] Write integration test for `GET /api/v1/lecs-hosts` covering pagination, filters, auth in `backend/tests/integration/test_lecs_host_api.py`
- [ ] T017 [US2] Write integration test for `DELETE /api/v1/lecs-hosts/{id}` covering success, 404, 403 in `backend/tests/integration/test_lecs_host_api.py`

### Implementation for User Story 2

- [ ] T018 [US2] Implement `list_hosts(user_id, page, page_size, region, status, search)` async service function with pagination (math.ceil pattern), SQLAlchemy query with user_id + status + region + name ILIKE filtering, soft-delete exclusion (deleted_at IS NULL) in `backend/src/app/services/lecs_host_service.py`
- [ ] T019 [US2] Implement `delete_host(user_id, host_id)` async service function with ownership check, running-status guard (raise ValueError for `running` status), soft-deletion (set `deleted_at = now()`) in `backend/src/app/services/lecs_host_service.py`
- [ ] T020 [US2] Implement `validate_quota(user_id, quantity)` async service function counting active hosts (deleted_at IS NULL), checking user count + quantity ≤ 200 and quantity ≤ 100 in `backend/src/app/services/lecs_host_service.py`
- [ ] T021 [US2] Implement `GET /api/v1/lecs-hosts` endpoint with `page`, `page_size`, `region`, `status`, `search` query params, calling `list_hosts()`, returning `{"status": "success", "data": {"items": [...], "pagination": {...}}}` in `backend/src/app/api/lecs_host.py`
- [ ] T022 [US2] Implement `DELETE /api/v1/lecs-hosts/{host_id}` endpoint calling `delete_host()`, returning `{"status": "success", "data": {"host_id": "..."}}` in `backend/src/app/api/lecs_host.py`
- [ ] T023 [US2] Register `lecs_host_router` (prefix `/api/v1/lecs-hosts`, tags `["lecs-host"]`) in `backend/src/app/main.py`
- [ ] T024 [US2] Update list page template: add status dashboard (5 stat items with numeric counts), action toolbar (开机, 关机, 重启, 重置密码, 续费, 更多, 导出 — disabled for v1.0 except for placeholder), search/filter bar, data table headers matching design spec in `backend/frontend/templates/lecs_host_list.html`
- [ ] T025 [US2] Fetch host list data via `fetch()` to the list API on page load, render rows dynamically (or via Jinja2 server-side rendering with `hosts` context passed from route), show empty state with "购买弹性云服务器" button and region selector when count is 0 in `backend/frontend/templates/lecs_host_list.html` + inline script
- [ ] T026 [US2] Pass host list data and pagination context from route to template: update `GET /console/lecs-hosts/list` to call `list_hosts()` and pass `{"hosts": items, "stats": ..., "pagination": ...}` in `backend/src/app/main.py`
- [ ] T027 [P] [US2] Add LECS Host List page styles (status dashboard badges, action toolbar buttons, data table layout, empty state) to `backend/frontend/static/css/console.css`

**Checkpoint**: At this point, User Story 2 is fully functional. List page shows 5 stats, action toolbar, search filter, and a real data table populated from the database. Empty state with purchase button shown when no hosts. Pagination, region/status/name filters all working.

---

## Phase 5: User Story 3 — Create a New LECS Host (Priority: P2) 🎯

**Goal**: Users click "购买弹性云服务器" from the list page, navigate to `/console/lecs-hosts/create`, and configure 6 sections: 基础配置 (billing mode + region), 实例 (instance spec cards), 操作系统 (OS image grid), 公网访问 (public IP toggle + bandwidth), 购买量 (duration + quantity), then see total fees and click "立即购买" to submit.

**Independent Test**: Navigate to creation page, select billing mode "包年/包月/12个月", region "华北-北京四", instance type "高性价比型" with spec "x1.2u.4g", OS "Huawei Cloud EulerOS 2.0", enable public IP with 5 Mbps bandwidth, quantity 1, auto-renew off. Click "立即购买". Verify API call succeeds and host is created with `creating` status. Verify fee calculation matches expected total. Test form validation: try quantity 101 (blocked), try invalid bandwidth 3000 (blocked).

### Tests for User Story 3 ⚠️

- [ ] T028 [US3] Write unit test for `get_instance_types()` + `get_os_images()` catalog services in `backend/tests/unit/test_lecs_host_service.py`
- [ ] T029 [US3] Write unit test for `create_host()` service covering happy path, quota exceeded, validation errors, price calculation in `backend/tests/unit/test_lecs_host_service.py`
- [ ] T030 [US3] Write integration test for `GET /api/v1/instance-types` and `GET /api/v1/os-images` catalog endpoints in `backend/tests/integration/test_lecs_host_api.py`
- [ ] T031 [US3] Write integration test for `POST /api/v1/lecs-hosts` covering happy path, 400 validation, 409 quota in `backend/tests/integration/test_lecs_host_api.py`

### Implementation for User Story 3

- [ ] T032 [US3] Implement `get_instance_types()` async service function returning all instance types + their specs grouped by category in `backend/src/app/services/lecs_host_service.py`
- [ ] T033 [US3] Implement `get_os_images()` async service function returning available OS images sorted by `sort_order` in `backend/src/app/services/lecs_host_service.py`
- [ ] T034 [US3] Implement `create_host(user_id, request)` async service function with: quota validation, validation rules (duration required for monthly, bandwidth 1-2000, valid spec/image refs), IP address allocation (private IP generation, public IP if enabled), price calculation (`monthly_price × duration_multiplier × quantity`), record insertion with status `creating`, in `backend/src/app/services/lecs_host_service.py`
- [ ] T035 [US3] Implement `GET /api/v1/instance-types` endpoint returning `{"status": "success", "data": {"categories": {...}}}` grouped by economy/high_cost_performance/high_performance in `backend/src/app/api/lecs_host.py`
- [ ] T036 [US3] Implement `GET /api/v1/os-images` endpoint returning `{"status": "success", "data": {"images": [...]}}` in `backend/src/app/api/lecs_host.py`
- [ ] T037 [US3] Implement `POST /api/v1/lecs-hosts` endpoint with full body validation, calling `create_host()`, returning 201 with `{"status": "success", "data": {"host_id": ..., "name": ..., "status": "creating", "price_amount": ...}}` in `backend/src/app/api/lecs_host.py`
- [ ] T038 [US3] Add `GET /console/lecs-hosts/create` route handler (HTMLResponse) protected by `require_auth`, returning `lecs_host_create.html` template in `backend/src/app/main.py`
- [ ] T039 [US3] Create `lecs_host_create.html` Jinja2 template with 6 configuration sections: 基础配置 (计费模式 radio: 包年/包月 + 按需计费, region select), 实例 (3 type tabs: 经济型/高性价比型/高性能型, spec cards with vCPU/memory/disk/price + selected border highlight), 操作系统 (13-image grid with icons: Huawei EulerOS, CentOS, SUSE, Ubuntu, Debian, OpenSUSE, AlmaLinux, Rocky Linux, CentOS Stream, CoreOS, openEuler, SUSE SAP, Windows + version dropdown below grid + 主机安全防护 checkbox) in `backend/frontend/templates/lecs_host_create.html`
- [ ] T040 [US3] Continue template: 公网访问 section (toggle checkbox, bandwidth billing radio: 按带宽计费/按流量计费, bandwidth size button group: 1/2/5/10/100/200/自定义 Mbps + range note "1-2,000 Mbit/s"), 购买量 section (duration buttons: 1-12月, 1年, 2年, 3年 + 自动续费 checkbox + 扣款规则/续费时长 links; quantity number input with +/- buttons, max 100, quota note "最多可以创建200台. 一次最多可以创建100台"), 配置费用说明与购买 section (total price display ¥XXX.XX, 了解计费详情 link, 立即购买 black round button) in `backend/frontend/templates/lecs_host_create.html`
- [ ] T041 [US3] Add client-side JavaScript for form state management: selection sync (highlight selected spec card/OS image/button group), price recalculation on each change (fetch or inline computed), form validation (bandwidth 1-2000, qty 1-100, duration required for monthly), submission handler (POST to `/api/v1/lecs-hosts` with JSON body, show success/error notification, redirect to list on success) inline in `backend/frontend/templates/lecs_host_create.html`
- [ ] T042 [P] [US3] Add LECS Host Create page styles (6-section card layout, spec card hover/selected states, OS image grid layout, price display fixed footer bar, responsive) to `backend/frontend/static/css/console.css`
- [ ] T043 [US3] Add "购买弹性云服务器" button to the list page empty state and toolbar that navigates to `GET /console/lecs-hosts/create` in `backend/frontend/templates/lecs_host_list.html`

**Checkpoint**: All user stories are now independently functional. Complete creation workflow: user selects all 6 configuration sections → price updates → submits → host created with `creating` status → redirected to list page. Form validation blocks invalid inputs.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T044 [P] Add `data-testid` attributes to ALL interactive components on lecs_host_list.html: list-level stats (lecs-host-stat-alert etc.), action buttons (lecs-host-action-start etc.), search input (lecs-host-search-input), purchase button (lecs-host-buy-button), region selector (lecs-host-region-selector), row checkboxes (lecs-host-row-checkbox) — per spec Section 3.2 table in `backend/frontend/templates/lecs_host_list.html`
- [ ] T045 [P] Add `data-testid` attributes to ALL interactive components on lecs_host_create.html: billing mode radio (lecs-billing-mode), region select (lecs-region-selector), instance type tabs (lecs-instance-type-tabs), spec cards (lecs-instance-card-{id}), instance spec tag (lecs-instance-spec-tag), custom buy link (lecs-instance-custom-link), OS image grid (lecs-os-image-grid), OS image cards (lecs-os-image-{name}), OS version select (lecs-os-version-selector), security checkbox (lecs-host-security-checkbox), security info link (lecs-host-security-info-link), public access toggle (lecs-public-access-toggle), bandwidth billing radio (lecs-bandwidth-billing), bandwidth size buttons (lecs-bandwidth-size), custom bandwidth input (lecs-bandwidth-custom), duration buttons (lecs-purchase-duration), auto-renew checkbox (lecs-auto-renew-checkbox), purchase quantity input (lecs-purchase-quantity), price display (lecs-config-price), price details link (lecs-price-details-link), buy submit button (lecs-buy-submit-button) — per spec Section 3.2 table in `backend/frontend/templates/lecs_host_create.html`
- [ ] T046 Write Playwright E2E test for list page: login → search "LECS主机" → click result → verify list page loads with empty state in `backend/tests/e2e/test_lecs_host_list.py`
- [ ] T047 Write Playwright E2E test for creation page: fill all 6 sections → submit → verify success notification and redirect to list page in `backend/tests/e2e/test_lecs_host_create.py`
- [ ] T048 [P] Run full test suite from project root: `cd backend && pytest tests/ --cov=src/app --cov-fail-under=90 -v` and verify all tests pass in `backend/tests/`
- [ ] T049 Run quickstart.md validation from project root: verify dev server starts, `localhost:8000/console/lecs-hosts/list` accessible, `localhost:8000/console/lecs-hosts/create` renders, API endpoints return expected schemas per `specs/007-lecs-hosts/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — already done from spec 006
- **Foundational (Phase 2)**: BLOCKS all user stories. Models, migration, schemas, and seed data must exist before any story-specific work
- **User Story 1 (Phase 3)**: Depends on Foundational only for the route/structure. Can proceed immediately after T001-T003 complete
- **User Story 2 (Phase 4)**: Depends on Foundational (models/schema in place). Can proceed in parallel with US1 after T008-T009 are done
- **User Story 3 (Phase 5)**: Depends on Foundational (InstanceType/Spec/OSImage models and seed data). Can proceed after T003-T005, T007 are done
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1) — Search & Navigate**: Standalone. Only needs console template modification + new route. No backend model dependency.
- **User Story 2 (P1) — List View**: Depends on LECSHost model + list/delete service + API endpoints. Independently testable once foundation is ready.
- **User Story 3 (P2) — Creation**: Depends on InstanceType/InstanceSpec/OSImage models + seeding + create service + API. Independently testable once foundation is ready.

### Within Each User Story

- Schema/model tasks before service tasks
- Service tasks before endpoint tasks
- Endpoint/integration before frontend template
- Template styling before client-side JS
- Full E2E after all templates are functional

### Parallel Opportunities

- **Foundational Phase**: T001, T003, T004, T005, T008, T009 are fully parallel (different files). T002 depends on T001 (same file). T006 depends on T001-T005 (migration needs all models). T007 depends on T003-T005 (seeding needs model data).
- **After Foundational**: US1, US2, US3 can all proceed in parallel.
- **US2 Backend**: T018, T019, T020 (services) are parallel (same file but independent functions). T021, T022 (API endpoints) parallel. T024, T027 (template + CSS) parallel.
- **US3 Backend**: T032, T033, T034 (services) parallel. T035, T036, T037 (endpoints) parallel. T039, T042 (template + CSS) parallel.
- **Polish**: T044, T045 (data-testid attributes) can run in parallel across two different files.

### Parallel Example: Foundational Phase

```bash
# Launch all independent model/schema tasks together:
Task T001: Enums in backend/src/app/models/lecs_host.py
Task T003: InstanceType model in backend/src/app/models/instance_type.py
Task T004: InstanceSpec model in backend/src/app/models/instance_type.py
Task T005: OSImage model in backend/src/app/models/instance_type.py
Task T008: Response schemas in backend/src/app/schemas/lecs_host.py
Task T009: Catalog schemas in backend/src/app/schemas/lecs_host.py
```

### Parallel Example: US2 Backend + Frontend

```bash
# After foundational is done, launch all US2 tasks in parallel across files:
# Backend service:
Task T018: list_hosts() in backend/src/app/services/lecs_host_service.py
Task T019: delete_host() in backend/src/app/services/lecs_host_service.py
Task T020: validate_quota() in backend/src/app/services/lecs_host_service.py
# Backend API:
Task T021: GET /api/v1/lecs-hosts in backend/src/app/api/lecs_host.py
Task T022: DELETE /api/v1/lecs-hosts/{id} in backend/src/app/api/lecs_host.py
# Frontend:
Task T024: List template in backend/frontend/templates/lecs_host_list.html
Task T027: Console CSS in backend/frontend/static/css/console.css
```

---

## Implementation Strategy

### MVP First (User Story 1 + User Story 2)

1. Complete Phase 2: Foundational (models, migration, schemas, seed data)
2. Complete Phase 3: User Story 1 (search + list page route + template shell)
3. Complete Phase 4: User Story 2 (list API + list page with data)
4. **STOP and VALIDATE**: Test search → navigate → list with data display
5. Demo: User can find LECS Host via search and see their hosts listed

### Incremental Delivery

1. Foundational complete → Models, migration, seed data ready
2. + User Story 1 → Search integration + list page shell → Test → Demo
3. + User Story 2 → List with real data, pagination, filters → Test → Demo (MVP!)
4. + User Story 3 → Creation workflow with 6 sections + price calculation → Test → Demo
5. + Polish → data-testid coverage + E2E tests + full test suite
6. Each phase adds value without breaking previous phases

### Parallel Team Strategy

With multiple developers after Foundational is done:

- **Developer A**: User Story 1 (search + route + template shell)
- **Developer B**: User Story 2 Backend (services + API + list template + CSS)
- **Developer C**: User Story 3 (independent — only needs T003-T005, T007 from foundational)

---

## Notes

- [P] tasks = different files, no cross-file dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- data-testid (T044, T045) is constitution-mandatory — do not skip
- Quota validation: 200 max hosts per user, 100 max per single request
- Bandwidth validation: 1-2000 Mbps range
- Private IP generation: use simple sequential approach (10.0.x.y) for v1.0
- v1.0 creation is synchronous — returns `creating` status immediately
- Rebranding: all "华为云" → "Lee云" in instance type/OS image seed data (use "Lee云" branding in any descriptive text)

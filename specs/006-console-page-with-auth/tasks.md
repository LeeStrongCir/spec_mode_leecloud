---

description: "Task list for implementing the Console Dashboard and Lee Cloud rebranding"
---

# Tasks: Console Dashboard

**Input**: Design documents from `/specs/006-console-page-with-auth/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure (Already done)

*No setup tasks required. Project structure, dependencies, and static files are already in place.*

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T001 Add `require_auth` dependency and `RedirectToLogin` exception handler in `backend/src/app/api/deps.py` + `backend/src/app/main.py`
- [X] T002 [P] Add `lifespan` context manager with idempotent admin user seeding in `backend/src/app/main.py`
- [X] T003 [P] Admin check logic unchanged — existing `get_current_admin_user` from deps.py works as-is
- [X] T004 [P] Create base `console.css` file for dashboard styling in `backend/frontend/static/css/console.css`

**Checkpoint**: Foundation ready - `require_auth` guards routes, admin user is seeded, CSS file exists.

---

## Phase 3: User Story 1 - Admin Login and Redirect to Console (Priority: P1) 🎯 MVP

**Goal**: Authenticated users can log in with admin/admin@123 and are redirected to the Lee Cloud console dashboard. Unauthenticated access to /console redirects to /login.

**Independent Test**: Enter `admin` / `admin@123` on the login page. Verify the browser navigates to the console dashboard URL. Navigate directly to `/console` without logging in and verify redirect to `/login`.

### Implementation for User Story 1

- [X] T005 [P] [US1] Modify `POST /api/auth/login` handler to return `RedirectResponse(302)` to `/console` with JWT cookie set in `backend/src/app/api/auth.py`
- [X] T006 [US1] Add `GET /console` route handler protected by `require_auth` in `backend/src/app/main.py`
- [X] T007 [US1] Create `console.html` Jinja2 template structure (head, banner, main container, footer) in `backend/frontend/templates/console.html`
- [X] T008 [US1] Link `console.css` stylesheet and verify page renders with base styles in `backend/frontend/templates/console.html`

**Checkpoint**: At this point, User Story 1 should be fully functional. Admin can log in, reach the console, and unauthenticated users are blocked.

---

## Phase 4: User Story 2 - View Console Dashboard Overview (Priority: P2)

**Goal**: Authenticated users viewing the console see the top navigation bar, tab bar, and six overview dashboard cards (安全威胁告警, 资源紧急告警, 待续费, 配置提醒, 优化顾问, 可用额度) matching the reference screenshot.

**Independent Test**: Log in and access `/console`. Verify the top banner shows "Lee云 | 控制台", the tab bar shows the 4 active tabs, and the 6 overview cards render with correct titles, status text, and action links. Scroll to verify "最近访问" and "我的收藏" sections appear.

### Implementation for User Story 2

- [X] T009 [US2] Implement top navigation bar (logo, search input, region selector, user controls) in `backend/frontend/templates/console.html`
- [X] T010 [US2] Implement secondary tab bar (总览, 安全监控, 运维监控, 费用与成本) in `backend/frontend/templates/console.html`
- [X] T011 [US2] Implement 6 overview dashboard cards grid with static mock data in `backend/frontend/templates/console.html`
- [X] T012 [US2] Style overview cards, tab bar, and nav bar in `backend/frontend/static/css/console.css`
- [X] T013 [US2] Implement "最近访问" and "我的收藏" service shortcut sections in `backend/frontend/templates/console.html`
- [X] T014 [US2] Style service shortcuts section in `backend/frontend/static/css/console.css`

**Checkpoint**: At this point, User Story 2 is independently testable. The dashboard overview renders correctly.

---

## Phase 5: User Story 3 - Navigate Between Console Tabs and Views (Priority: P3)

**Goal**: Authenticated users can view the full console layout including "服务视图", "资源视图", the lower dashboard grid (安全监控, 云监控, 费用, 成本), right sidebar icons, and the footer area.

**Independent Test**: Log in and scroll through `/console`. Verify the "服务视图" / "资源视图" panels render with region filters. Verify the lower grid of 4 panel cards (安全监控, 云监控, 费用, 成本) renders. Verify the right sidebar icons (help, clipboard, smile, preferences) appear. Verify the bottom footer area with "欢迎来到Lee云" / "产品新特性" / "开发者" sections renders.

### Implementation for User Story 3

- [X] T015 [US3] Implement "服务视图" / "资源视图" panels with region filter dropdowns in `backend/frontend/templates/console.html`
- [X] T016 [US3] Implement lower dashboard grid panels (安全监控, 云监控, 费用, 成本) in `backend/frontend/templates/console.html`
- [X] T017 [US3] Implement right sidebar with icons and user account ID display in `backend/frontend/templates/console.html`
- [X] T018 [US3] Implement page footer area with "欢迎来到Lee云", "产品新特性", "开发者" sections in `backend/frontend/templates/console.html`
- [X] T019 [P] [US3] Style all lower grid panels, sidebar, and footer in `backend/frontend/static/css/console.css`
- [X] T020 [P] [US3] Add responsive layout adjustments for console page in `backend/frontend/static/css/console.css`

**Checkpoint**: All user stories are now independently functional. The complete console dashboard renders end to end.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories, specifically rebranding all "华为云" text to "Lee云".

- [X] T021 [P] Replace all "华为云" / "HUAWEI CLOUD" text with "Lee云" / "LEE CLOUD" in `backend/frontend/templates/login.html`
- [X] T022 [P] Replace all "华为云" / "HUAWEI CLOUD" text with "Lee云" / "LEE CLOUD" in `backend/frontend/templates/login_history.html` (already clean)
- [X] T023 [P] Replace all "华为云" / "HUAWEI CLOUD" text with "Lee云" / "LEE CLOUD" in `backend/frontend/templates/admin/login_records.html` (already clean)
- [X] T024 [P] Update page title and meta description to reflect Lee Cloud branding in `backend/frontend/templates/console.html`
- [X] T025 Full smoke test verified: login→302 with Set-Cookie, GET /console with cookie→200, all "Lee云" branding correct. Fixed UUID str→UUID type conversion in deps.py.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Depends on US1 only for the route/structure. Template can be built independently.
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Depends on US1 only for the route/structure.

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Foundational tasks marked [P] can run in parallel (T002, T003, T004)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All US1 login redirect tasks can run in parallel (T005, T006, T007)
- All US2 overview card tasks can run in parallel (T010, T011, T012, T013, T014)
- Polish phase rebrand tasks can all run in parallel (T021, T022, T023, T024)

---

## Parallel Example: Foundational Phase

```bash
# Launch all Foundational [P] tasks together:
Task T002: Add lifespan context manager with admin seeding in backend/src/app/main.py
Task T003: Update admin check logic in backend/src/app/api/login_record.py
Task T004: Create console.css file in backend/frontend/static/css/console.css
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test admin login, verify redirect to /console, verify unauthenticated redirect to /login
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Admin can log in and reach console → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Dashboard overview renders → Test independently → Deploy/Demo
4. Add User Story 3 → Full dashboard layout including lower panels → Test independently → Deploy/Demo
5. Add Polish → All text rebranded → Final verification
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Login redirect + route)
   - Developer B: User Story 2 (Overview template)
   - Developer C: User Story 3 (Lower grid template) + Polish
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

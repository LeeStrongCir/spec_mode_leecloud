# Research: LECS Hosts Management

**Date**: 2026-05-09
**Feature**: 007-lecs-hosts

## R-001: Async Task Execution Approach

**Context**: The spec requires async lifecycle operations (create ~30s, shutdown/start ~10s, delete ~5s). The project has no task queue infrastructure (no Celery/RQ configured).

**Decision**: Use `asyncio.create_task()` with in-memory state tracking managed by a service layer. Each async operation will:
1. Write the transitional state to DB immediately (e.g., `creating`, `shutting_down`)
2. Spawn a background task with explicit `await asyncio.sleep()` to simulate processing time
3. Update DB to final state upon completion (or timeout fallback)

**Rationale**: 
- The project has no message queue dependency; introducing one would be premature.
- `asyncio.create_task()` is lightweight, already available in the FastAPI async runtime.
- The existing `user_agent_service.py` pattern in the project shows async service methods are already in use.
- Tasks are tracked via a simple `Dict[uuid, asyncio.Task]` registry keyed by host ID, allowing cancellation and status querying.
- For production scale beyond v1.0, the abstraction layer allows swapping to Celery without changing API contracts.

**Alternatives considered**:
- **Celery/RQ integration**: Would require Redis/RabbitMQ, worker processes, and significant infrastructure setup. Overkill for v1.0.
- **Simple polling simulation**: Client-side only with no server-side state writes. Would fail to persist state across server restarts and would break if the user refreshes.
- **Database-level job queue with periodic scheduler**: More robust but requires additional infrastructure (APScheduler, crontab entry, or similar).

**Risk mitigation**: Background tasks register with a cleanup routine. Server restart causes all `creating`/`shutting_down`/`starting`/`deleting` hosts to be reset to their appropriate fallback states via the lifespan startup handler.

---

## R-002: State Machine Implementation

**Context**: 8 states need specific transition rules enforced at both API (409/403 responses) and frontend (button disabled) levels.

**Decision**: Define a static state transition matrix as a Python dict mapping each state to allowed operations. The API service layer checks this matrix before executing any lifecycle operation. Frontend logic mirrors the same matrix in JavaScript for immediate button state.

**State Machine Matrix**:

| Current State | Allowed Operations | Next State(s) |
|--------------|-------------------|---------------|
| `creating` | None (lock) | `normal` (success) / `failed` (timeout/error) |
| `normal` | `shutdown` | `shutting_down` |
| `normal` | `delete` — **blocked** (front-end disabled) | — |
| `failed` | `start` | `starting` |
| `failed` | `delete` | `deleting` |
| `shutting_down` | None (lock) | `stopped` |
| `stopped` | `start` | `starting` |
| `stopped` | `delete` | `deleting` |
| `starting` | None (lock) | `normal` |
| `deleting` | None (lock) | `deleted` (soft delete) |
| `deleted` | None (hidden from list) | — |

**API Enforcement**: Each lifecycle endpoint checks the current state against allowed states. If mismatch, returns `HTTPException(status_code=409)` with a descriptive error message. The frontend never sends disallowed requests (buttons are disabled), but the API must defend regardless.

**Frontend Enforcement**: A JavaScript state machine object maps each status value to `canShutdown`, `canStart`, `canDelete` booleans. The render function applies the `disabled` attribute accordingly.

**Rationale**: A declarative matrix is easier to maintain, test, and reason about than scattered if/else guards. Both Python and JS implementations share the same logical structure.

**Alternatives considered**:
- **Transition function per state**: Each state is a class with a `next_state(operation)` method. More extensible but over-engineered for 8 states.
- **Database-level constraints**: A CHECK constraint limiting transitions. Would provide ultimate safety but requires raw SQL enums and is harder to modify.

---

## R-003: Console Search Integration

**Context**: `console.html` has a vanilla JS `serviceCatalog` array with categorized service items. Need to add "LECS主机" as a searchable entry that routes to `/console/lecs-hosts/list`.

**Decision**: Add a new entry in the `serviceCatalog` array under the "控制台" category:

```javascript
{ name: 'LECS主机', action: '计算', type: 'ecs', url: '/console/lecs-hosts/list' }
```

Modify the `renderResults` function's click handler to respect the `url` field and navigate. The existing code already has a pattern for this with the `item.url` check in the click handler:

```javascript
const clickHandler = item.url ? ` onclick="window.location.href='${item.url}'"` : '';
```

This pattern exists but is not triggered because no items currently have `url` properties. Adding `url: '/console/lecs-hosts/list'` to the LECS host catalog entry will activate this existing routing pattern.

**Rationale**: Minimal change to existing code. The routing infrastructure is already present, just needs data population. Maintains consistency with the existing search implementation.

---

## R-004: Form Validation Approach

**Context**: The creation page has complex validation (hostname regex, credential complexity, IP format, mask range). Needs real-time feedback.

**Decision**: Client-side JavaScript validation with visual feedback. On "立即购买" click, all validations run client-side first. On submit, the server performs the same validations (defense in depth). Form validation errors display as red text below the respective input fields.

**Validation rules implemented in two places**:
1. **Client-side** (`lecs-hosts.js`): Regex-based immediate validation on `input`/`change` events. Shows/hides error messages with CSS class toggling.
2. **Server-side** (API route): Pydantic schema validation + custom validator functions. Returns `422 Unprocessable Entity` with field-level error messages that the client renders.

**Rationale**:
- Client-side provides instant user feedback without round-trip latency.
- Server-side ensures data integrity (client validation can be bypassed).
- The project's existing `schemas/auth.py` pattern uses Pydantic models for body validation, which extends naturally to LECS host create schemas.
- No htmx needed — the entire creation flow is a form submission → API call → redirect pattern, simpler and more consistent with the existing login/form flow.

**Alternatives considered**:
- **htmx with server-side validation**: Would add a new dependency (htmx) and require server round-trips for each field validation. Overkill for v1.0.
- **HTMX + Alpine.js**: Would modernize the SSR approach but adds two new JavaScript dependencies.

---

## R-005: Cost Calculation Strategy

**Context**: Spec requires real-time cost display. Frontend calculates estimated cost in the confirmation dialog. Backend is the source of truth for actual billing.

**Decision**: Frontend calculates cost on-demand from the selected instance spec price and billing mode/duration. The formula is straightforward arithmetic (price × months for subscription, price ÷ 30 for on-demand). Instance spec prices are hardcoded in the frontend (matching the spec's defined prices) and also stored in the backend for consistency validation.

**Frontend**: Pure JS calculation triggered on any spec/billing-mode/duration change. Updates the cost display area instantly.

**Backend**: The create API endpoint receives `billing_mode` + `spec_id` + `duration` and recalculates cost for the final order. Stores `cost_info` as a JSON snapshot in the DB for audit trails.

**Rationale**: Simple arithmetic has zero risk of front-end calculation error. Hardcoding prices on the front-end is acceptable because the spec defines fixed prices. For future dynamic pricing, a backend `GET /api/v1/lecs-hosts/pricing` endpoint can be added.

---

## R-006: List Page Polling Strategy

**Context**: Frontend must poll for status updates when hosts are in transitional states.

**Decision**: Use `setInterval` at 3-second intervals, but only active when `creating`, `shutting_down`, `starting`, or `deleting` hosts exist in the current page state. The polling function:
1. Calls `GET /api/v1/lecs-hosts` (same list endpoint)
2. Compares returned statuses with current DOM state
3. Updates affected rows (status badge, button states)
4. Clears interval when no transitional states remain

**Rationale**: Simple and matches existing patterns. No event-source or WebSocket needed for ~3-second polling granularity. The polling cost is negligible given the short-lived nature of transitional states.

---

## Consolidated Decisions

| # | Decision | Chosen Approach |
|---|---------|----------------|
| R-001 | Async execution | `asyncio.create_task()` with in-memory registry |
| R-002 | State machine | Declarative dict matrix (Python + JS mirror) |
| R-003 | Console search | Add `url` field to existing `serviceCatalog` |
| R-004 | Form validation | Client-side JS + server-side Pydantic (dual) |
| R-005 | Cost calculation | Frontend arithmetic for display; backend for actual |
| R-006 | List polling | `setInterval` 3s when transitional states exist |

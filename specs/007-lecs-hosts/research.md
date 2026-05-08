# Research: LECS Host Management

## Technical Decisions

### Decision 1: LECS Host Model Design
**Decision**: LECSHost is a new SQLAlchemy model stored in the `lecs_hosts` table, with a `user_id` foreign key to the existing `User` model. Status is stored as `SAEnum` with values `creating`, `running`, `stopped`, `error`, `deleted`. Soft-delete via `deleted_at` column. Billing mode stored as enum (`monthly`/`hourly`).

**Rationale**: Follows the existing model pattern (User, LoginRecord, Session). Uses `SAEnum` for type safety. Soft-delete aligns with the "Recycle Bin" tab in the UI design. `user_id` scoping enables multi-tenant isolation.

**Alternatives considered**:
- Hard delete → Rejected: UI shows a "Recycle Bin" tab, implies soft deletion
- Direct instance_type embedding → Rejected: Separating InstanceSpec into its own table allows future spec updates without migration

### Decision 2: Instance Types & OS Images Storage
**Decision**: Instance types and OS images are static configuration tables seeded at startup, not user-editable entities. Two models: `InstanceType` (economy/high-cost-performance/high-performance) and `InstanceSpec` (concrete vCPU/memory/disk/price configuration). OS images stored in `OSImage` model.

**Rationale**: Cloud providers don't expose instance type definitions as mutable end-user resources. Seeding at startup (via `lifespan` like the admin user seed) ensures they're always available. Keeps the API surface small.

**Alternatives considered**:
- Config file (YAML/JSON) → Rejected: Database allows future admin management via a management API
- Remote API to "real" cloud provider → Deferred: v1.0 is mock/static; real provider integration is future scope

### Decision 3: API Response Format
**Decision**: LECS Host API endpoints return a consistent wrapper format:
- List: `{"status": "success", "data": {...}, "pagination": {"total": N, "page": P, "page_size": S, "pages": P}}`
- Create: `{"status": "success", "data": {"host_id": "...", "name": "...", "status": "creating"}}`
- Delete: `{"status": "success", "data": {"host_id": "..."}}`

**Rationale**: Matches the existing pattern used by `login_record.py` API endpoints. Consistent with `fastapi.Response` best practices. Pagination uses `math.ceil()` for total pages calculation (existing pattern).

**Alternatives considered**:
- Pydantic `GenericResponse` wrapper → Rejected: The existing codebase uses plain dicts (no response wrapper model), so we follow the established pattern

### Decision 4: Region Handling
**Decision**: v1.0 hardcodes region to "华北-北京四" (North China-Beijing-4). The region selector UI element is displayed but is functionally a no-op. Backend APIs filter by this fixed region value.

**Rationale**: The spec's Assumptions section states "Region selection is initially fixed to 华北-北京四, with multi-region support planned for a future version." This minimizes complexity while preserving the UI layout for future expansion.

**Alternatives considered**:
- Full multi-region support → Deferred: Requires infrastructure provider abstraction and regional resource routing
- Region from user profile → Rejected: No user profile system exists yet

### Decision 5: LECS Host Creation is Synchronous for v1.0
**Decision**: The `create_host()` service function creates the LECSHost row synchronously with status `creating` and returns immediately. The frontend shows a success notification and navigates back to the list page. The status transition to `running` would be handled by a background worker (future scope).

**Rationale**: Cloud server provisioning is inherently async. A synchronous API that returns `creating` status provides immediate feedback without requiring a polling mechanism or WebSocket infrastructure (which don't exist in the current codebase). The list page will display hosts with `creating` status.

**Alternatives considered**:
- Background Celery/RQ worker → Deferred: Requires message broker infrastructure not present
- Polling endpoint → Deferred: Adds endpoint complexity for v1.0

### Decision 6: Pricing Calculation
**Decision**: Pricing is computed by the backend service using a deterministic formula: `(instance_spec.monthly_price × duration_multiplier) × quantity × quantity_discount`. The frontend fetches the total from the backend during creation submission.

**Rationale**: Pricing must be authoritative (cannot be set by the frontend). The service computes it at creation time and stores it as `price_amount` on the host record for audit purposes.

**Alternatives considered**:
- Frontend calculates → Rejected: Security risk (price manipulation); backend must be authoritative
- External pricing service → Deferred: v1.0 static pricing; external service is future scope

### Decision 7: Console Search Integration
**Decision**: The LECS Host menu item is added to the existing console template's search results data structure (likely inline JavaScript or template variable). The search functionality itself is not being rebuilt — only the "LECS Host" option is added to the existing search results set.

**Rationale**: The existing console page already implements search functionality. Adding "LECS Host" as a new search result entry is the minimal change. The existing search JS handles keyword matching and click navigation.

**Alternatives considered**:
- New search index/API → Rejected: Over-engineering for a single menu item addition
- Separate search page → Rejected: The console search bar already exists

### Decision 8: Jinja2 Template Structure for Creation Page
**Decision**: The creation page uses a single long-scroll Jinja2 template with 6 visual sections separated by headings and cards. Form data is submitted via a single POST to the creation API. Each section uses standard HTML form elements with `name` attributes for binding.

**Rationale**: The design screenshots show a single-page long form. A single POST submission is the simplest and most reliable approach for SSR. Section-by-section client-side validation would require a JS framework (not in scope for v1.0).

**Alternatives considered**:
- Multi-step wizard with client-side state → Rejected: Requires client-side framework (out of scope)
- Section-by-section API calls → Rejected: Would require session state management on the backend

## Resolved NEEDS CLARIFICATION Items

### From Source Requirements (Section 9):

1. **LECS Host Lifecycle Management** → Resolved as: v1.0 only supports creation and deletion. List page action buttons (Start, Stop, Restart, Reset Password) are present but non-functional (disabled or hidden). This follows the "不包含" (excludes) section of the requirements document.

2. **Public IP Binding** → Resolved as: Public IP is created and bound at host creation time. The public IP address is assigned during the `create_host()` service call. This aligns with industry-standard cloud provider patterns.

3. **Creation Flow Interaction Mode** → Resolved as: Single-page long form (Option A), matching the provided design screenshots. Six configuration sections are rendered in a scrollable page with the purchase button at the bottom.

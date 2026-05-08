# Feature Specification: LECS Hosts Management

**Feature Branch**: `007-lecs-hosts`  
**Created**: 2026-05-09  
**Status**: Draft  
**Input**: User description: "LECS主机（云服务器）功能开发：支持在控制台搜索、列表查看、创建、开关机控制及删除操作，前端页面风格与控制台保持一致"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Search and Navigate to LECS Hosts List (Priority: P1)

After logging into the Lee Cloud Platform console, a user types "LECS主机" or "云服务器" in the top search bar. The search results intelligently match and display a "LECS Hosts" entry with highlighted keywords. Clicking the entry navigates directly to the LECS hosts list page.

**Why this priority**: This is the primary entry point for all LECS host functionality. Without discoverable navigation, users cannot access any host management features.

**Independent Test**: Can be fully tested by searching for "LECS" or "云服" in the console search bar and verifying the result appears with highlighted keywords, then clicking to confirm navigation to the list page.

**Acceptance Scenarios**:

1. **Given** the user is logged into the console, **When** they type "LECS" or "云服" in the search bar, **Then** the dropdown results display "LECS主机" with the search term highlighted.
2. **Given** the search results show "LECS主机", **When** the user clicks the entry, **Then** the browser navigates to the LECS hosts list page and it loads successfully.

---

### User Story 2 - View LECS Hosts List with Action Matrix (Priority: P1)

Upon entering the list page, the user sees a data table displaying host information: host name/ID, billing mode, runtime status (color-coded badges), private IP, and an action column. The page header includes only a "Create ECS Host" button on the right—no global toolbar. The action column contains **Shutdown**, **Start**, and **Delete** buttons. Button availability strictly follows a state machine: operations not supported by the current host state are automatically grayed out and disabled. Hosts marked as "deleted" do not appear in the list.

**Why this priority**: The list page is the central resource management interface. Accurate status visualization and precise action controls are essential for safe operations.

**Independent Test**: Create hosts in different states (normal, creating, stopped, deleting, etc.) and verify status badge rendering, action button enable/disable logic, and soft-deleted hosts' list visibility.

**Acceptance Scenarios**:

1. **Given** the list page has data, **When** the user views the action column, **Then** each row displays "Shutdown", "Start", and "Delete" buttons.
2. **Given** a host is in "Normal" state, **When** viewing the action column, **Then** "Shutdown" is clickable; "Start" and "Delete" are grayed out.
3. **Given** a host is in "Stopped" state, **When** viewing the action column, **Then** "Start" and "Delete" are clickable; "Shutdown" is grayed out.
4. **Given** a host is in "Creation Failed" state, **When** viewing the action column, **Then** only "Delete" is clickable; others are grayed out.
5. **Given** a host is "Deleting", **When** viewing the action column, **Then** the status shows "Deleting" and all action buttons are grayed out.
6. **Given** a host has been deleted, **When** the user refreshes the list page, **Then** the host no longer appears in the list.

---

### User Story 3 - Create a LECS Host (Priority: P2)

From the list page, the user clicks "Create ECS Host" to enter the creation page. They configure six sections in sequence: Basic Configuration (billing mode, hostname, access credentials), Instance Configuration (instance type and specific spec), Operating System (image selection), IP Configuration (DHCP or manual), Purchase Duration, and Cost Confirmation. After reviewing all choices in a confirmation dialog, they submit the creation. The front-end immediately returns to the list page showing "Creating" status, while the back-end completes resource provisioning within 30 seconds, ultimately transitioning to "Normal" or "Creation Failed".

**Why this priority**: Resource delivery is the core user path. Form complexity and cost calculation accuracy directly impact user conversion.

**Independent Test**: Complete the full creation flow, verify form validation, confirm dialog content completeness, and verify list page status refresh after submission.

**Acceptance Scenarios**:

1. **Given** the user is on the list page, **When** they click "Create ECS Host", **Then** the creation page loads showing six configuration sections, purchase duration selector, and a cost display area.
2. **Given** all form fields pass validation, **When** the user clicks "Buy Now" and confirms in the dialog (showing the full configuration summary including duration and cost), **Then** the host quota check passes, the page navigates to the list, and the new host appears with "Creating" status.

---

### User Story 4 - Control Host Lifecycle (Shutdown/Start) (Priority: P3)

From the list page's action column, the user clicks "Shutdown" or "Start" based on the host's current state. When "Normal", clicking "Shutdown" transitions the status to "Shutting Down" asynchronously (approximately 10 seconds), then completes to "Stopped". When "Stopped" or "Creation Failed", clicking "Start" transitions to "Starting" (approximately 10 seconds), then completes to "Normal". During any intermediate state ("Creating", "Shutting Down", "Starting", "Deleting"), all action buttons are disabled to prevent conflicting operations.

**Why this priority**: Enables users to control service availability—stopping services for cost savings (stop-and-save) or recovering from failures.

**Independent Test**: Cover the complete state machine flow: Normal → Shutting Down → Stopped → Starting → Normal, verifying async timing and conflict prevention logic.

**Acceptance Scenarios**:

1. **Given** a host is "Normal", **When** the user clicks "Shutdown", **Then** the button immediately grays out, status changes to "Shutting Down". After approximately 10 seconds, status becomes "Stopped" and "Start" becomes available.
2. **Given** a host is "Stopped", **When** the user clicks "Start", **Then** the button grays out, status changes to "Starting". After approximately 10 seconds, status becomes "Normal" and "Shutdown" becomes available.
3. **Given** a host is in "Shutting Down" transitional state, **When** the user clicks "Shutdown" or "Start", **Then** buttons are disabled and the system rejects any duplicate requests.

---

### User Story 5 - Safely Delete a Host (Priority: P4)

From the list page, the user deletes a host under strict state restrictions. Delete is only permitted when the host is fully stopped ("Stopped") or in an error state ("Creation Failed"). After clicking "Delete", a confirmation dialog appears. Upon confirmation, the host status changes to "Deleting" asynchronously (2–5 seconds). The operation performs a soft delete: the host record is retained in the database but filtered out from the list view, and the quota count decreases by 1.

**Why this priority**: Completes the host lifecycle. Restricting deletion to stopped/error states prevents data loss and resource leaks. The async mechanism ensures smooth front-end experience and eventual state consistency.

**Independent Test**: Verify that normal-state hosts cannot be deleted, stopped-state hosts trigger async deletion, and quota is successfully released.

**Acceptance Scenarios**:

1. **Given** a host is "Normal", "Creating", or "Shutting Down", **When** the user attempts to delete, **Then** the button is grayed out or clicking shows the message "Please shut down the host before deleting" and blocks submission.
2. **Given** a host is "Stopped" or "Creation Failed", **When** the user clicks "Delete" and confirms the dialog, **Then** status changes to "Deleting", all action buttons gray out. After 3–5 seconds, the row disappears from the list and the top quota count decreases by 1.

---

### Edge Cases

- **Quota limit**: When the user's total host count (including all non-deleted records: normal, shutting down, stopped, creation failed, deleting) reaches **100**, creation is blocked with the message "Host count limit reached".
- **Timeout degradation**: If the back-end creation task exceeds timeout (> 60s), the host status is forcibly degraded to "Creation Failed" and front-end polling stops to prevent infinite "Creating" loops.
- **Concurrency lock**: While a row is in an async operation (shutting down, deleting, etc.), the action column buttons are strictly disabled, blocking any clicks.
- **Network disconnection**: Operations attempted during network loss trigger a full list refresh (refetch) upon reconnection, ensuring display state is consistent with the database.
- **Billing on stopped hosts (on-demand mode)**: When a host is "Stopped" in on-demand billing, compute resources (CPU/RAM) are released and billing stops, but storage resources (disk/image) continue to incur storage fees.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a searchable entry point in the console search bar that matches "LECS主机" and "云服务器" with keyword highlighting, and navigates to the LECS hosts list page upon click.
- **FR-002**: The system MUST display a list of hosts in a data table showing host name/ID, billing mode, runtime status, private IP, and an action column with shutdown, start, and delete buttons.
- **FR-003**: The system MUST enforce a state machine for action button availability: only operations compatible with the current host state are enabled; all others are disabled and visually grayed out.
- **FR-004**: The system MUST provide a multi-step host creation form with six configuration sections: Basic Configuration, Instance Configuration, Operating System, IP Configuration, Purchase Duration, and Cost Confirmation.
- **FR-005**: The system MUST validate hostname format (alphanumeric and underscore, 4–10 characters, not starting with underscore) with real-time error feedback.
- **FR-006**: The system MUST validate access credentials: username (alphanumeric and special characters, 4–16 characters) and password (alphanumeric and special characters, 8–32 characters) with real-time error feedback.
- **FR-007**: The system MUST offer two instance types (Economy and High-Performance) with multiple specific spec options, each displaying vCPU, RAM, system disk, and monthly price.
- **FR-008**: The system MUST provide an OS image selector with "Huawei Euler OS", "Ubuntu", and "Windows" options, defaulting to "Huawei Euler OS".
- **FR-009**: The system MUST support two IP allocation modes: DHCP (no additional input) and Manual Configuration (requiring valid IP address and subnet mask 8–24).
- **FR-010**: The system MUST calculate and display estimated costs in real-time: for subscription billing (instance price × months, displayed per month), and for on-demand billing (instance price ÷ 30, displayed per day).
- **FR-011**: The system MUST display a confirmation dialog summarizing all user selections including total cost before submitting the creation request.
- **FR-012**: The system MUST enforce a maximum quota of 100 hosts per user (counting all records where deleted_at is null, including normal, stopping, stopped, failed, and deleting states).
- **FR-013**: The system MUST perform asynchronous lifecycle operations (create, shutdown, start, delete) with intermediate transitional states before reaching terminal states.
- **FR-014**: The system MUST filter soft-deleted hosts from the list view while retaining their records in the database.
- **FR-015**: The system MUST automatically refresh host status at short intervals when any host is in a transitional state (creating, shutting down, starting, deleting), and stop refreshing when all hosts reach terminal states.
- **FR-016**: The system MUST log all host lifecycle operations (create, delete, start, shutdown) including operator, timestamp, IP address, and operation details.
- **FR-017**: The system MUST require authentication for all LECS host operations, with admin users managing all hosts and regular users managing only their own hosts.
- **FR-018**: The system MUST encrypt sensitive data (IP configuration, password hashes) in storage and apply data masking to logs.

### Key Entities

- **LECS Host**: A virtual computing instance that represents a cloud server. Key attributes include: unique identifier, owner/user, hostname, billing mode (subscription or on-demand), runtime status (creating, normal, failed, shutting down, stopped, starting, deleting, deleted), instance specification (vCPU, RAM, system disk), operating system image, IP configuration, purchase duration, cost snapshot, soft-deletion timestamp, and error message (for failed operations).
- **Instance Spec**: A configurable hardware specification defining the computing resources allocated to a host. Includes instance type (Economy or High-Performance), vCPU count, RAM size, system disk size, and monthly price.
- **User Quota**: A per-user limit on the total number of hosts (up to 100) that determines whether new host creation is permitted. Counts all non-deleted host records.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can find "LECS Hosts" in the console search results and navigate to the list page within 1 second of typing.
- **SC-002**: The LECS hosts list page loads completely (including status data and action columns) within 2 seconds.
- **SC-003**: List page state transitions operate with 100% accuracy—no stuck states or state desynchronization between front-end and database.
- **SC-004**: Action button enable/disable logic matches the state machine matrix with 100% accuracy—zero accidental triggers of invalid operations.
- **SC-005**: The delete operation rejects requests for hosts in non-stopped/non-failed states with 100% interception rate.
- **SC-006**: 100% of interactive components have `data-testid` attributes for automated testing coverage.

## Assumptions

- Target users are cloud platform customers with basic technical knowledge to configure virtual servers (IP, OS, instance specs).
- Desktop-only support (1280px and above); tablet and mobile support are out of scope for v1.0.
- Existing authentication system and user session management will be reused (JWT cookie authentication).
- Existing CSRF protection and API rate limiting mechanisms will be applied to LECS host APIs.
- Cost display on the front-end is for user reference only; actual billing is determined by the back-end order generation.
- Compute resource billing stops when a host is stopped in on-demand mode, but storage billing continues (disk and image retention fees apply).
- Password policy does not require mixed case letters—alphanumeric and special characters with 8–32 length is sufficient.
- The async task queue infrastructure (e.g., Celery/RQ) exists and supports scheduling tasks with 30s create, 10s shutdown/start, and 5s delete durations.
- Instance spec data and OS image data sources are internally available and provide accurate pricing information.
- "Restart" operation (shutdown + start combination) is out of scope for v1.0.

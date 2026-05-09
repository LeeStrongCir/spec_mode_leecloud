# Feature Specification: Console Dashboard

**Feature Branch**: `006-console-page-with-auth`  
**Created**: 2026-05-07  
**Status**: Draft  
**Input**: User description: "1、创建控制台页，按照华为云控制台.png 的内容和样式来创建 2、设置管理员初始账号密码：admin/admin@123 3、当登录页登录成功时，跳转到控制台页 4、所有'华为云'相关字眼全改为'Lee云'"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Admin Login and Redirect to Console (Priority: P1)

An administrator logs in with the default credentials (admin/admin@123). After successful authentication, the system redirects to the Lee Cloud console dashboard page.

**Why this priority**: This is the primary user flow — without login and redirect, the entire console feature is inaccessible.

**Independent Test**: Can be fully tested by entering admin/admin@123 on the login page and verifying the browser navigates to the console dashboard URL.

**Acceptance Scenarios**:

1. **Given** the user is on the login page, **When** they enter username "admin" and password "admin@123", **Then** the system authenticates successfully and redirects to the console dashboard
2. **Given** the user is on the login page, **When** they enter incorrect credentials, **Then** an error message is displayed and they remain on the login page
3. **Given** the user has valid session cookies from a previous login, **When** they navigate to the console path directly, **Then** they are shown the console dashboard without re-authenticating

---

### User Story 2 - View Console Dashboard Overview (Priority: P2)

An authenticated user views the console dashboard, which displays a comprehensive overview of cloud resources, security status, cost summary, and recent activity — matching the Huawei Cloud console layout.

**Why this priority**: The dashboard is the core value proposition — it provides the user with an at-a-glance view of all cloud services and resources.

**Independent Test**: Can be fully tested by logging in and verifying all dashboard sections render correctly with proper data display.

**Acceptance Scenarios**:

1. **Given** the user is authenticated, **When** they access the console page, **Then** they see a top navigation bar with Lee Cloud branding, search bar, and user controls
2. **Given** the user is on the console, **When** they view the "Total Overview" tab, **Then** they see cards for security alerts, pending payments, reminders, and available quota
3. **Given** the user is on the console, **When** they scroll down, **Then** they see the service view, resource view, security monitoring, cloud monitoring, cost, and cost forecast sections

---

### User Story 3 - Navigate Between Console Tabs and Views (Priority: P3)

An authenticated user switches between different console sections — 总览 (Overview), 安全监控 (Security Monitoring), 运维监控 (Operations Monitoring), 费用与成本 (Costs and Expenses) — to view different aspects of their cloud environment.

**Why this priority**: Navigation between tabs provides access to all management capabilities; without it, the user is limited to a single view.

**Independent Test**: Can be fully tested by clicking each tab and verifying the corresponding content panel is displayed.

**Acceptance Scenarios**:

1. **Given** the user is on the console, **When** they click the "安全监控" tab, **Then** the security monitoring panel becomes active and displays relevant content
2. **Given** the user is on the console, **When** they click the "费用与成本" tab, **Then** the cost and billing panel becomes active
3. **Given** the user is on the console, **When** they use the search bar, **Then** they can search for services, resources, documents, APIs, and solutions

---

### Edge Cases

- What happens when an unauthenticated user navigates directly to the console URL? (Should be redirected to login page)
- How does system handle invalid default admin credentials (e.g., default password should be changeable)?
- What happens when the admin deletes their own account?
- How does the console behave when rendered on narrow screens (< 768px)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST create an admin user with username "admin" and password "admin@123" during initial database setup
- **FR-002**: System MUST redirect authenticated users from `/login` to `/console` upon successful login
- **FR-003**: System MUST redirect unauthenticated users from `/console` to `/login` (protected route)
- **FR-004**: System MUST display a top navigation bar with: Lee Cloud logo, "控制台" text, region selector, search bar
- **FR-005**: System MUST display a secondary tab bar with four sections: 总览 (Overview), 安全监控 (Security Monitoring), 运维监控 (Operations Monitoring), 费用与成本 (Costs and Expenses)
- **FR-006**: System MUST render dashboard cards for: 全生命周期安全防护, 暂未配置告警, 待续费, 配置提醒, 优化顾问, 可用额度
- **FR-007**: System MUST render "最近访问" (Recent Access) and "我的收藏" (My Favorites) sections with service shortcuts
- **FR-008**: System MUST render "服务视图" (Service View) and "资源视图" (Resource View) panels with region filters
- **FR-009**: System MUST render a grid of lower dashboard panels: 安全监控 (Security), 云监控 (Cloud Monitoring), 费用 (Cost), 成本 (Cost Analysis)
- **FR-010**: System MUST render a footer area with 欢迎来到Lee云 (Welcome to Lee Cloud), 产品新特性 (New Features), and 开发者 (Developer) sections
- **FR-011**: System MUST update all occurrences of "华为云" to "Lee云" and "HUAWEI CLOUD" to "LEE CLOUD" across all existing pages (login, templates, headers, footers)
- **FR-012**: System MUST update the Huawei Cloud login page banner text from "华为云" to "Lee云"
- **FR-013**: System MUST update the login page footer text from "华为云首页" to "Lee云首页"
- **FR-014**: System MUST update the login page banner header from "华为云" to "Lee云"
- **FR-015**: System MUST render the right sidebar with action icons: help, clipboard, smile/settings, preferences
- **FR-016**: System MUST render the user avatar placeholder and account ID in the top-right corner of the console

### Key Entities *(include if feature involves data)*

- **User (Admin)**: Represents the system administrator account with elevated permissions. Key attributes: unique username, hashed password, role (admin), creation timestamp.
- **Session**: Represents an authenticated user session tracked via JWT cookie. Key attributes: user reference, creation time, expiry time, refresh capability.
- **Dashboard Section**: Represents a content panel within the console. Key attributes: title, icon/color, status text, action link, associated data type.
- **Service Card**: Represents a cloud service shortcut (e.g., VPC, ECS, BMS, AS, OBS). Key attributes: service name, icon, description, link URL.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Admin user (admin/admin@123) can log in and reach the console dashboard within 2 seconds of form submission
- **SC-002**: 100% of "华为云" and "HUAWEI CLOUD" references in the user-facing UI are replaced with "Lee云" and "LEE CLOUD" respectively
- **SC-003**: All six dashboard overview cards render with correct title, status text, and action links matching the reference screenshot layout
- **SC-004**: Unauthenticated users attempting to access `/console` are redirected to `/login` within 1 second
- **SC-005**: The console dashboard renders without horizontal scroll at viewport widths of 1280px and above
- **SC-006**: Console page structure matches the five major layout zones: top nav, tab bar, overview cards, middle service/resource panels, lower dashboard grid, bottom welcome/features panel

## Assumptions

- The admin user will be seeded via a database migration or startup script — not via the user-facing registration flow
- The console page is a read-only dashboard view (no CRUD operations needed at this stage)
- Region selector dropdown values are static placeholders (e.g., 华北-北京四) and do not need backend data binding
- The right sidebar icons (help, clipboard, settings) are decorative/action placeholders without backend integration
- The dashboard data (costs, security alerts, resources) is static/mock data for the initial implementation — real data binding is out of scope
- The "华为云服务" subtitle text on the login page left panel should be changed to "Lee云服务" to maintain consistency
- Existing JWT authentication mechanism is reused without modification to token format or cookie names

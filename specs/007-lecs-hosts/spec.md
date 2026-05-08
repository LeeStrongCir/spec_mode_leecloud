# Feature Specification: LECS Host Management

**Feature Branch**: `007-lecs-hosts`  
**Created**: 2026-05-08  
**Status**: Draft  
**Input**: User description: "LECS主机（云服务器）功能开发：支持在控制台搜索、列表查看、创建/删除/查询LECS主机，前端页面风格与控制台保持一致"  
**Source**: `reqs/需求规格说明书-LECS主机.md`

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Search and Navigate to LECS Host List from Console (Priority: P1)

A logged-in administrator or standard user searches for "LECS Host" or "Cloud Server" in the top search bar of the Lee Cloud Console. The search results display a "LECS Host" option. Clicking the result navigates the user directly to the LECS Host List page.

**Why this priority**: This is the primary entry point for users to discover and access the LECS Host management feature. Without this, users cannot find the feature at all.

**Independent Test**: Can be fully tested by entering "LECS主机" or "云服务器" in the console search bar, confirming the "LECS主机" option appears in results, clicking it, and verifying the browser navigates to the LECS Host List page.

**Acceptance Scenarios**:

1. **Given** the user is logged into the console, **When** they type "LECS主机" in the search bar, **Then** the search results show a "LECS主机" option with the matching keyword highlighted
2. **Given** the user is logged into the console, **When** they type "云服务器" (synonym) in the search bar, **Then** the search results show a "LECS主机" option as a synonym match
3. **Given** the search results display the "LECS主机" option, **When** the user clicks on it, **Then** the browser navigates to the LECS Host List page

---

### User Story 2 - View LECS Host List with Status Dashboard (Priority: P1)

A logged-in user accesses the LECS Host List page and sees a comprehensive status dashboard with five statistics (Monitoring Alerts, Security Risks, Pending Renewals, UniAgent Not Installed, Configuration Reminders), action buttons for bulk operations, a search/filter bar for finding hosts by name, and a data table with columns: Name/ID, Monitoring, Security, Status, Availability Zone, Spec/Image, Operation Group, IP Address, Billing Mode, Tags, and Actions. If no hosts exist in the current region, an empty state is displayed with a "Purchase Elastic Cloud Server" button.

**Why this priority**: The list page is the central management interface for all LECS Host operations. Every subsequent action originates from here.

**Independent Test**: Can be fully tested by navigating to the LECS Host List page URL and verifying: the two tab options (Cloud Servers / Recycle Bin), the five status statistics display, the action buttons (Start, Stop, Restart, Reset Password, Renew, More, Export), the search filter bar, the table column headers match the reference design, and when no data exists, the empty state with the purchase button and region selector is shown.

**Acceptance Scenarios**:

1. **Given** the user is authenticated and in region "华北-北京四", **When** they access the LECS Host List page, **Then** the page displays two tabs: "云服务器" (selected by default) and "回收站"
2. **Given** the user is viewing the LECS Host List page, **When** they look at the status dashboard, **Then** they see five statistics: 监控告警, 安全风险, 待续费, 未安装UniAgent, 配置提醒 — all showing numeric counts
3. **Given** the user views the list page actions toolbar, **When** they look at available buttons, **Then** they see: 开机 (Start), 关机 (Stop), 重启 (Restart), 重置密码 (Reset Password), 续费 (Renew), 更多 (More dropdown), 导出 (Export dropdown)
4. **Given** the current region has no LECS Host data, **When** the user views the table area, **Then** an empty state is displayed with: an empty box icon, text "暂无表格数据", region explanation text, a "购买弹性云服务器" button, and a region dropdown selector
5. **Given** the current region has LECS Host data, **When** the user views the table area, **Then** a data grid is displayed with rows containing host information and per-row action links

---

### User Story 3 - Create a New LECS Host (Priority: P2)

A logged-in user clicks the "购买弹性云服务器" (Purchase Elastic Cloud Server) button on the LECS Host List page. They are taken to the LECS Host Creation page, which guides them through six configuration sections in sequence: Basic Configuration (billing mode and region), Instance Selection (compute spec with vCPU/memory/disk), OS Image Selection (choose from available OS images), Public Network Access (elastic public IP and bandwidth configuration), Purchase Quantity (duration and number of instances), and finally the Configuration Fees display with a "立即购买" (Purchase Now) submit button.

**Why this priority**: Creating cloud server instances is the core value proposition of this feature. Users obtain computing resources through this workflow.

**Independent Test**: Can be fully tested by navigating to the creation page, configuring each section (billing mode, region, instance spec, OS image, public network access, purchase duration and quantity), verifying the total fee updates dynamically with each selection change, and confirming the submission flow triggers a creation request.

**Acceptance Scenarios**:

1. **Given** the user is on the LECS Host List page, **When** they click "购买弹性云服务器", **Then** they are navigated to the LECS Host Creation page
2. **Given** the user is on the Creation page, **When** they view the layout, **Then** they see six configuration sections in order: 基础配置 (Basic Config), 实例 (Instance), 操作系统 (OS), 公网访问 (Public Network Access), 购买量 (Purchase Quantity), and 配置费用说明与购买 (Config Fees & Purchase)
3. **Given** the user configures each section's options, **When** they change any selection, **Then** the configuration fees display updates to reflect the current total
4. **Given** the user has completed all configuration sections, **When** they click "立即购买", **Then** a creation request is submitted and a success or error notification is displayed to the user

---

### Edge Cases

- What happens when an unauthenticated user directly navigates to the LECS Host List page URL? → Should be redirected to the login page
- How does the system handle creation errors returned by the backend API? → Display specific error messages to the user (quota exceeded, invalid parameters, etc.)
- What is displayed when the current region has no LECS Host data? → Show an empty state page with a prompt and a "Purchase Elastic Cloud Server" button
- What happens when the purchase quantity exceeds the user's quota (200 hosts)? → Block submission and prompt the user with a quota exceeded message plus an application entry for expansion
- What happens when a single creation request exceeds 100 hosts? → Block submission and prompt "一次最多可以创建100台云服务器"
- What happens when a public IP is required but resources are insufficient? → Display a friendly error message to the user
- What happens when a user attempts to delete a running LECS Host? → Confirm if the user wants to stop the host first before deletion

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow users to find "LECS Host" via the console search bar using both "LECS主机" and "云服务器" (synonym) as search terms
- **FR-002**: System MUST display the LECS Host List page with two tabs: "云服务器" and "回收站", defaulting to "云服务器"
- **FR-003**: System MUST display five status statistics on the list page: 监控告警 (Monitoring Alerts), 安全风险 (Security Risks), 待续费 (Pending Renewals), 未安装UniAgent (UniAgent Not Installed), 配置提醒 (Configuration Reminders)
- **FR-004**: System MUST display action buttons on the list page: 开机 (Start), 关机 (Stop), 重启 (Restart), 重置密码 (Reset Password), 续费 (Renew), 更多 (More), 导出 (Export)
- **FR-005**: System MUST display a data table with columns: 名称/ID, 监控, 安全, 状态, 可用区, 规格/镜像, 操作组, IP地址, 计费模式, 标签, 操作
- **FR-006**: System MUST display an empty state with a purchase button when no LECS Host data exists in the selected region
- **FR-007**: System MUST provide a search/filter bar on the list page that filters hosts by name
- **FR-008**: System MUST provide a region selector dropdown on the list page empty state
- **FR-009**: System MUST navigate users to the LECS Host Creation page when they click "购买弹性云服务器"
- **FR-010**: System MUST display six configuration sections on the Creation page in order: 基础配置 (Billing Mode + Region), 实例 (Instance Spec Selection), 操作系统 (OS Image Selection), 公网访问 (Public Network Access), 购买量 (Purchase Duration + Quantity), 配置费用说明与购买 (Fees Display + Purchase Button)
- **FR-011**: System MUST support two billing modes: 包年/包月 (Monthly/Yearly Prepaid) and 按需计费 (On-Demand/Postpaid)
- **FR-012**: System MUST provide instance type tabs: 经济型 (Economy), 高性价比型 (High Cost-Performance), 高性能型 (High Performance), with multiple spec cards under each showing vCPU, memory, system disk, and monthly price
- **FR-013**: System MUST provide a grid of OS image choices including Huawei Cloud EulerOS, CentOS, SUSE, Ubuntu, Debian, OpenSUSE, AlmaLinux, Rocky Linux, CentOS Stream, CoreOS, openEuler, SUSE SAP, and Windows
- **FR-014**: System MUST provide public network access toggle with bandwidth billing mode (按带宽计费/按流量计费) and bandwidth size selection (1-2000 Mbps)
- **FR-015**: System MUST provide purchase duration selection (1-12 months, 1-3 years) and purchase quantity (1-100), with auto-renewal option for prepaid billing
- **FR-016**: System MUST display the total configuration fees dynamically and provide a link to billing details
- **FR-017**: System MUST support the backend API for creating a new LECS Host instance with full configuration parameters
- **FR-018**: System MUST support the backend API for deleting an existing LECS Host instance
- **FR-019**: System MUST support the backend API for querying LECS Hosts with pagination, region filter, status filter, and name search
- **FR-020**: System MUST add `data-testid` attributes to all interactive components on the LECS Host pages (buttons, inputs, selects, checkboxes, radio groups, etc.)
- **FR-021**: System MUST enforce quota limits: maximum 200 hosts per user, maximum 100 hosts per single creation request
- **FR-022**: System MUST enforce bandwidth range: 1-2000 Mbps
- **FR-023**: System MUST require host security protection to be enabled by default during creation (configurable)

### Key Entities *(include if feature involves data)*

- **LECS Host**: A cloud server instance created and managed by a user. Key attributes: unique ID, name, status, region, billing mode, instance spec, OS image, public/private IP addresses, security settings, auto-renewal flag, quantity, creation/expiry timestamps.
- **Instance Spec**: A computing configuration template defining vCPU count, memory size, system disk type and capacity, and monthly price. Belongs to an instance type (Economy / High Cost-Performance / High Performance).
- **OS Image**: An operating system template used when creating a host. Key attributes: image name, OS family, version, architecture, default disk size.
- **User**: The account owner who creates and manages LECS Hosts. Has a quota limit for maximum number of hosts.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can find "LECS Host" via the console search bar and navigate to the list page within 1 second of entering search text
- **SC-002**: The LECS Host List page loads fully (including statistics and empty state or data table) within 2 seconds
- **SC-003**: Users can complete the LECS Host creation workflow and successfully submit a creation request within 30 seconds
- **SC-004**: 100% of interactive components on the LECS Host pages have a `data-testid` attribute assigned
- **SC-005**: The visual style (color scheme, typography, spacing, interaction patterns) of the LECS Host pages is consistent with the existing Console Dashboard pages
- **SC-006**: API response times for list query, create, and delete operations are under 500ms at P95 percentile
- **SC-007**: Quota validation (max 200 hosts) and single-request validation (max 100 hosts) correctly block submission when limits would be exceeded

## Assumptions

- Users have stable internet connectivity for normal access to the Lee Cloud platform
- v1.0 does NOT include start/stop/restart/reset password operations for LECS Hosts — these will be provided in subsequent versions
- The existing user authentication system (JWT Cookie) is reused without adding new auth logic
- Instance spec data (Economy, High Cost-Performance, High Performance types) and OS image data are provided by the backend; the frontend only renders and allows selection
- Region selection is initially fixed to "华北-北京四", with multi-region support planned for a future version
- Public IP allocation and bandwidth management are handled automatically by the underlying infrastructure
- Pricing logic is computed by the backend and returned; the frontend only displays the calculated fees
- Host creation is an asynchronous operation; the frontend notifies the user of completion after the backend finishes creating the instance

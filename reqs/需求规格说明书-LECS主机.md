# Lee云平台 需求规格说明书

**需求编号**: 007-LECS主机  
**创建日期**: 2026-05-08  
**状态**: 草稿  
**需求描述**: "LECS主机（云服务器）功能开发：支持在控制台搜索、列表查看、创建/删除/查询LECS主机，前端页面风格与控制台保持一致"

---

## 一、业务背景与目标

### 1.1 业务背景
Lee云平台作为云计算服务平台，需要提供基础的云服务器（LECS主机）管理能力，让用户能够创建、管理和运维虚拟计算实例。这是云平台的核心服务能力，为用户提供弹性的计算资源。

### 1.2 业务目标
- 提供云服务器的创建、查看、删除等基础管理功能
- 提供直观的云资源配置界面，支持多种实例规格和操作系统选择
- 支持公网访问配置，满足不同业务场景的网络需求
- 提供清晰的计费信息展示，便于用户预估成本

### 1.3 范围界定
- **包含**: 控制台搜索集成、LECS主机列表页、LECS主机创建页（含基础配置、实例选择、操作系统选择、公网访问配置、购买量配置、费用与购买按钮）、后端API接口（查询、创建、删除）
- **不包含**: LECS主机的启动/停止/重启操作、主机安全监控、数据盘管理、快照备份、主机详情查看与编辑、批量操作、主机标签管理、区域切换功能

---

## 二、用户场景与验收 *(必填)*

### 用户故事 1 - 在控制台搜索并跳转至LECS主机列表页 (优先级: P1)

用户登录Lee云平台控制台后，在顶部搜索栏输入"LECS主机"或"云服务器"，搜索结果中出现"LECS主机"选项，点击后直接跳转至LECS主机列表页。

**优先级理由**: 这是用户访问LECS主机功能的主要入口，没有此入口用户将无法找到后续功能。

**独立可测**: 可通过在控制台搜索栏输入关键词并验证跳转来完整测试。

**验收场景**:

1. **前提**: 用户已登录控制台，**操作**: 在搜索栏输入"LECS主机"，**预期**: 搜索结果中出现"LECS主机"选项，高亮匹配关键词
2. **前提**: 用户已登录控制台，**操作**: 在搜索栏输入"云服务器"，**预期**: 搜索结果中出现"LECS主机"选项（"云服务器"为同义词匹配）
3. **前提**: 搜索结果中显示了"LECS主机"选项，**操作**: 用户点击该搜索结果，**预期**: 浏览器跳转至LECS主机列表页 `/console/lecs-hosts/list`

---

### 用户故事 2 - 查看LECS主机列表 (优先级: P1)

用户进入LECS主机列表页后，可以看到当前区域下的所有云服务器列表，包括主机名称/ID、监控状态、安全状态、运行状态、规格/镜像、IP地址、计费模式、标签等信息，同时可以看到统计面板（监控告警、安全风险、待续费、未安装UniAgent、配置提醒）。

**优先级理由**: 列表页是用户管理主机的核心界面，所有后续操作都从这里出发。

**独立可测**: 可通过访问列表页URL验证页面结构和内容显示。

**验收场景**:

1. **前提**: 用户已登录且当前区域为"华北-北京四"，**操作**: 访问LECS主机列表页，**预期**: 页面顶部显示"云服务器"标签页和"回收站"标签页，默认选中"云服务器"
2. **前提**: 用户查看LECS主机列表页，**操作**: 查看页面内容，**预期**: 页面显示统计项：监控告警 0、安全风险 0、待续费 0、未安装UniAgent 0、配置提醒 0；显示操作按钮：开机、关机、重启、重置密码、续费、更多、导出；显示搜索过滤栏"默认按照名称搜索、过滤"；显示列表列：名称/ID、监控、安全、状态、可...、规格/镜像、操作、IP地址、计费模式、标签、操作
3. **前提**: 当前区域无LECS主机数据，**操作**: 查看页面内容，**预期**: 显示空状态页面：空数据图标、"暂无表格数据"文字、"当前区域 华北-北京四 暂无数据，您可以购买弹性云服务器，或切换区域"说明文字、"购买弹性云服务器"按钮和区域下拉选择器
4. **前提**: 当前区域有LECS主机数据，**操作**: 查看列表内容，**预期**: 显示主机数据表格，每行包含主机信息和操作入口

---

### 用户故事 3 - 创建LECS主机 (优先级: P2)

用户在LECS主机列表页点击"购买弹性云服务器"或"创建"按钮后，进入LECS主机创建页，通过依次配置基础配置（计费模式、区域）、实例规格（CPU/内存/磁盘选择）、操作系统镜像选择、公网访问配置（弹性公网IP、带宽计费方式、带宽大小）、购买量（时长、数量），最终查看配置费用并点击"立即购买"完成创建。

**优先级理由**: 创建是云服务器功能的核心价值体现，用户通过此功能获得计算资源。

**独立可测**: 可通过完整填写创建表单并验证最终费用计算来测试。

**验收场景**:

1. **前提**: 用户在LECS主机列表页，**操作**: 点击"购买弹性云服务器"按钮，**预期**: 跳转至LECS主机创建页 `/console/lecs-hosts/create`
2. **前提**: 用户在LECS主机创建页，**操作**: 查看页面内容，**预期**: 页面包含配置板块：基础配置、实例、操作系统、公网访问、购买量、配置费用与购买按钮
3. **前提**: 用户在LECS主机创建页，**操作**: 配置计费模式、区域、实例规格、操作系统、公网访问、购买量，**预期**: 各配置板块按顺序显示，选择更新时配置费用同步更新
4. **前提**: 用户完成所有配置，**操作**: 点击"立即购买"按钮，**预期**: 提交创建请求，显示创建成功/失败提示

---

### 边界场景

- 当用户未登录时尝试访问LECS主机列表页，应重定向至登录页
- 当后端API返回创建错误时，前端应显示具体的错误信息提示用户
- 当当前区域无LECS主机数据时，列表页应显示空状态引导页面
- 当购买数量超过配额限制（200台）时，应提示用户超出配额并提供申请扩容入口
- 当单次创建数量超过限制（100台）时，应提示用户最多创建100台
- 当创建的主机需要公网IP但资源不足时，应有友好的错误提示
- 当用户删除正在运行的LECS主机时，应确认是否先停止再删除

---

## 三、前端需求

### 3.1 页面结构

| 页面名称 | 路由路径 | 页面描述 | 权限要求 |
|---------|---------|---------|---------|
| LECS主机列表页 | /console/lecs-hosts/list | LECS主机列表管理，包含统计面板、操作按钮、搜索过滤、数据表格 | 登录用户 |
| LECS主机创建页 | /console/lecs-hosts/create | LECS主机创建流程，包含基础配置、实例、操作系统、公网访问、购买量、费用确认 | 登录用户 |

### 3.2 交互组件标识（data-testid 规范）

> 根据项目宪法，所有可交互组件必须添加 `data-testid` 属性。

**LECS主机列表页**:

| 页面/模块 | 组件类型 | data-testid | 说明 |
|----------|---------|------------|------|
| lecs-host-list | tab | lecs-hosts-tab | 云服务器标签页 |
| lecs-host-list | tab | lecs-hosts-recycle-bin-tab | 回收站标签页 |
| lecs-host-list | stat-item | lecs-host-stat-alert | 监控告警统计项 |
| lecs-host-list | stat-item | lecs-host-stat-security | 安全风险统计项 |
| lecs-host-list | stat-item | lecs-host-stat-expiring | 待续费统计项 |
| lecs-host-list | stat-item | lecs-host-stat-uniagent | 未安装UniAgent统计项 |
| lecs-host-list | stat-item | lecs-host-stat-config | 配置提醒统计项 |
| lecs-host-list | button | lecs-host-action-start | 开机按钮 |
| lecs-host-list | button | lecs-host-action-stop | 关机按钮 |
| lecs-host-list | button | lecs-host-action-restart | 重启按钮 |
| lecs-host-list | button | lecs-host-action-reset-password | 重置密码按钮 |
| lecs-host-list | button | lecs-host-action-renew | 续费按钮 |
| lecs-host-list | button | lecs-host-action-more | 更多操作按钮 |
| lecs-host-list | button | lecs-host-action-export | 导出按钮 |
| lecs-host-list | input | lecs-host-search-input | 搜索过滤输入框 |
| lecs-host-list | button | lecs-host-buy-button | 购买弹性云服务器按钮 |
| lecs-host-list | select | lecs-host-region-selector | 区域下拉选择器 |
| lecs-host-list | checkbox | lecs-host-row-checkbox | 行选中复选框 |

**LECS主机创建页**:

| 页面/模块 | 组件类型 | data-testid | 说明 |
|----------|---------|------------|------|
| lecs-host-create | radio-group | lecs-billing-mode | 计费模式选择（包年/包月、按需计费） |
| lecs-host-create | select | lecs-region-selector | 区域选择下拉框 |
| lecs-host-create | tab-group | lecs-instance-type-tabs | 实例类型标签（经济型、高性价比型、高性能型） |
| lecs-host-create | card | lecs-instance-card-{id} | 具体实例规格卡片 |
| lecs-host-create | spec-tag | lecs-instance-spec-tag | 当前规格信息标签 |
| lecs-host-create | custom-link | lecs-instance-custom-link | 自定义购买链接 |
| lecs-host-create | image-grid | lecs-os-image-grid | 操作系统镜像选择网格 |
| lecs-host-create | image-card | lecs-os-image-{os-name} | 具体操作系统镜像卡片 |
| lecs-host-create | select | lecs-os-version-selector | 操作系统版本下拉选择 |
| lecs-host-create | checkbox | lecs-host-security-checkbox | 主机安全防护复选框 |
| lecs-host-create | link | lecs-host-security-info-link | 主机安全防护信息链接 |
| lecs-host-create | toggle | lecs-public-access-toggle | 公网访问开关 |
| lecs-host-create | radio-group | lecs-bandwidth-billing | 带宽计费方式（按带宽计费、按流量计费） |
| lecs-host-create | button-group | lecs-bandwidth-size | 带宽大小选择按钮组 |
| lecs-host-create | input | lecs-bandwidth-custom | 自定义带宽输入框 |
| lecs-host-create | button-group | lecs-purchase-duration | 购买时长按钮组 |
| lecs-host-create | checkbox | lecs-auto-renew-checkbox | 自动续费复选框 |
| lecs-host-create | link | lecs-auto-renew-rules-link | 扣款规则/续费时长链接 |
| lecs-host-create | number-input | lecs-purchase-quantity | 购买数量输入（含+-按钮） |
| lecs-host-create | price-display | lecs-config-price | 配置费用显示 |
| lecs-host-create | link | lecs-price-details-link | 了解计费详情链接 |
| lecs-host-create | button | lecs-buy-submit-button | 立即购买按钮 |

**命名规则**:
- 格式：`[功能模块]-[元素类型]` 或 `[功能模块]-[操作]-[元素类型]`
- 使用小写英文单词，以连字符 `-` 分隔
- 名称需清晰表达元素用途，避免 `div1`、`btn2` 等无意义命名

### 3.3 状态要求

**列表页**:
- 加载状态: 显示骨架屏或加载动画，表格区域显示加载状态
- 成功状态: 正常显示主机数据列表，显示选中行和操作按钮
- 失败状态: 显示错误提示，如"数据加载失败，请刷新重试"
- 空状态: 显示空数据图标、提示文字和引导按钮（购买弹性云服务器）

**创建页**:
- 加载状态: 规格/镜像等数据加载时显示加载动画
- 成功状态: 点击购买后显示创建成功提示，跳转至列表页
- 失败状态: 显示具体错误信息（如配额不足、参数校验失败等）
- 空状态: 各配置板块默认显示推荐选项

### 3.4 响应式要求

- 桌面端适配要求：1280px 及以上全功能展示
- 暂不支持平板端和移动端适配（v1.0 仅支持桌面端）

---

## 四、后端需求

### 4.1 API 接口

| 接口名称 | 请求方法 | 请求路径 | 权限要求 | 描述 |
|---------|---------|---------|---------|------|
| 查询LECS主机列表 | GET | /api/v1/lecs-hosts | JWT认证登录用户 | 分页查询当前用户/区域的LECS主机列表 |
| 创建LECS主机 | POST | /api/v1/lecs-hosts | JWT认证登录用户 | 根据配置参数创建新的LECS主机实例 |
| 删除LECS主机 | DELETE | /api/v1/lecs-hosts/{id} | JWT认证登录用户 | 删除指定的LECS主机实例 |

### 4.2 接口请求/响应

#### 4.2.1 查询LECS主机列表

- **请求方式**: `GET`
- **请求路径**: `/api/v1/lecs-hosts`
- **Content-Type**: `application/json`
- **认证方式**: `JWT Cookie`

**请求参数（Query）**:

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|-----|------|
| page | integer | 否 | 页码，默认 1 |
| page_size | integer | 否 | 每页数量，默认 20，最大 100 |
| region | string | 否 | 区域筛选，如 "华北-北京四" |
| status | string | 否 | 状态筛选：running / stopped / creating / error |
| search | string | 否 | 按名称/ID 模糊搜索 |

**成功响应 (200)**:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": "string - LECS主机唯一ID",
        "name": "string - 主机名称",
        "status": "string - 运行状态",
        "region": "string - 所在区域",
        "instance_type": "string - 实例规格",
        "os_name": "string - 操作系统名称",
        "public_ip": "string - 公网IP地址（可选）",
        "private_ip": "string - 私网IP地址",
        "billing_mode": "string - 计费模式：包年/包月 或 按需计费",
        "tags": "array - 标签列表"
      }
    ],
    "total": "integer - 总数",
    "page": "integer - 当前页码",
    "page_size": "integer - 每页数量"
  }
}
```

#### 4.2.2 创建LECS主机

- **请求方式**: `POST`
- **请求路径**: `/api/v1/lecs-hosts`
- **Content-Type**: `application/json`
- **认证方式**: `JWT Cookie`

**请求参数（Body - JSON）**:

| 参数名 | 类型 | 必填 | 说明 | 校验规则 |
|-------|------|-----|------|---------|
| name | string | 否 | 主机名称 | 最大 64 字符，可选 |
| region | string | 是 | 区域 | 有效区域值 |
| billing_mode | string | 是 | 计费模式：monthly（包年/包月）、hourly（按需计费） | 枚举值校验 |
| duration | integer | 条件必填 | 购买时长（月/年），按需计费时不需要 | 1-12个月或1-3年 |
| instance_type_id | string | 是 | 实例规格ID | 有效规格ID |
| os_image_id | string | 是 | 操作系统镜像ID | 有效镜像ID |
| enable_public_ip | boolean | 否 | 是否启用公网IP，默认 true | - |
| bandwidth_billing_mode | string | 条件必填 | 带宽计费模式：bandwidth（按带宽）、traffic（按流量） | 启用公网IP时必填 |
| bandwidth_mbps | integer | 条件必填 | 带宽大小 Mbps | 1-2000，启用公网IP时必填 |
| quantity | integer | 是 | 购买数量 | 1-100 |
| enable_security | boolean | 否 | 是否启用主机安全防护，默认 true | - |
| auto_renew | boolean | 否 | 是否自动续费，默认 false | 包年/包月时有效 |

**成功响应 (201)**:

```json
{
  "code": 201,
  "message": "success",
  "data": {
    "host_id": "string - 创建的主机ID",
    "name": "string - 主机名称",
    "status": "string - 初始状态：creating"
  }
}
```

#### 4.2.3 删除LECS主机

- **请求方式**: `DELETE`
- **请求路径**: `/api/v1/lecs-hosts/{host_id}`
- **认证方式**: `JWT Cookie`

**成功响应 (200)**:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "host_id": "string - 已删除的主机ID"
  }
}
```

**失败响应 (400/401/403/500)**:

| 状态码 | 错误码 | 错误信息 | 触发条件 |
|-------|-------|---------|---------|
| 400 | BAD_REQUEST | [错误信息] | 参数校验失败 |
| 401 | UNAUTHORIZED | 未授权访问 | 未登录或 Token 失效 |
| 403 | FORBIDDEN | 无权限操作 | 非主机所有者 |
| 404 | NOT_FOUND | 主机不存在 | 指定的主机ID不存在 |
| 409 | CONFLICT | 主机正在运行 | 需要先停止后才能删除 |
| 500 | INTERNAL_ERROR | [错误信息] | 服务器内部异常 |

### 4.3 数据模型

#### 实体：LECSHost（LECS主机）

LECS主机是用户创建和管理的云服务器实例，一个用户可拥有多个主机。

| 字段名 | 类型 | 必填 | 约束 | 说明 |
|-------|------|-----|------|------|
| id | UUID | 是 | PRIMARY KEY | 主机唯一标识 |
| user_id | UUID | 是 | FOREIGN KEY, INDEX | 所属用户ID |
| name | String(64) | 否 | - | 主机名称 |
| status | Enum | 是 | NOT NULL | 状态：creating / running / stopped / error / deleted |
| region | String(50) | 是 | NOT NULL, INDEX | 所在区域 |
| billing_mode | String(20) | 是 | NOT NULL | 计费模式：monthly / hourly |
| duration | Integer | 否 | - | 购买时长（月数） |
| expire_at | DateTime | 否 | - | 到期时间 |
| instance_type_id | String(50) | 是 | NOT NULL | 实例规格ID |
| os_image_id | String(50) | 是 | NOT NULL | 操作系统镜像ID |
| enable_public_ip | Boolean | 是 | DEFAULT true | 是否启用公网IP |
| bandwidth_billing_mode | String(20) | 否 | - | 带宽计费模式：bandwidth / traffic |
| bandwidth_mbps | Integer | 否 | CHECK 1-2000 | 带宽大小 |
| public_ip | String(45) | 否 | - | 公网IP地址 |
| private_ip | String(45) | 是 | NOT NULL | 私网IP地址 |
| enable_security | Boolean | 是 | DEFAULT true | 是否启用主机安全防护 |
| auto_renew | Boolean | 是 | DEFAULT false | 是否自动续费 |
| quantity | Integer | 是 | DEFAULT 1 | 购买数量 |
| price_amount | Decimal(10,2) | 否 | - | 单次购买金额 |
| created_at | DateTime | 是 | NOT NULL, DEFAULT now() | 创建时间 |
| updated_at | DateTime | 是 | NOT NULL, DEFAULT now() | 更新时间 |
| deleted_at | DateTime | 否 | SOFT DELETE | 软删除时间 |

#### 实体关系

- **User** 与 **LECSHost**: 1:N 关系，一个用户可以创建多个LECS主机
- **LECSHost** 与 **Order**: 1:N 关系（可选，如果系统已有订单模块），一个主机创建可关联一个订单记录

---

## 五、业务规则

### 5.1 核心功能要求

- **业务规则 1**: 系统 MUST 支持用户通过控制台搜索功能快速找到"LECS主机"功能入口
- **业务规则 2**: 系统 MUST 支持用户查看当前区域下的LECS主机列表和统计信息
- **业务规则 3**: 系统 MUST 支持用户创建LECS主机，包含基础配置、实例规格、操作系统、公网访问、购买量、费用确认等完整流程
- **业务规则 4**: 系统 MUST 支持用户删除LECS主机
- **业务规则 5**: 系统 MUST 支持用户查询LECS主机列表（分页、筛选）
- **业务规则 6**: 前端所有可交互组件 MUST 包含 `data-testid` 属性

### 5.2 数据校验规则

| 规则编号 | 规则描述 | 触发时机 | 处理策略 |
|---------|---------|---------|---------|
| VR-001 | 购买数量必须在 1-100 范围内 | 创建时 | 拦截提交，提示"一次最多可以创建100台云服务器" |
| VR-002 | 总主机数量（含本次）不能超过配额 200 台 | 创建时 | 拦截提交，提示配额超出并提供申请扩容入口 |
| VR-003 | 带宽大小必须在 1-2000 Mbps 范围内 | 创建时 | 拦截提交，提示带宽范围限制 |
| VR-004 | 计费模式和时长必须匹配（包年/包月需要时长，按需不需要） | 创建时 | 拦截提交，提示参数缺失 |
| VR-005 | 实例规格ID和操作系统镜像ID必须是有效值 | 创建时 | 拦截提交，提示无效配置 |

### 5.3 权限规则

| 角色 | 权限范围 | 可访问页面 | 可调用接口 | 操作限制 |
|-----|---------|-----------|-----------|---------|
| 管理员 (admin) | 管理所有LECS主机 | LECS主机列表页、LECS主机创建页 | 查询列表、创建、删除 | 无限制 |
| 普通用户 | 管理自己的LECS主机 | LECS主机列表页、LECS主机创建页 | 查询列表（仅自己）、创建（自己的）、删除（自己的） | 只能操作自己拥有的主机 |

### 5.4 安全要求

- **身份认证**: JWT Cookie 认证，Token 有效期内，复用现有认证机制
- **数据保护**: 敏感信息（如IP配置）需要加密存储
- **接口安全**: 复用现有 CSRF 保护和 API 限速机制
- **日志审计**: 所有LECS主机的创建和删除操作必须记录操作日志，包含操作人、操作时间、IP地址、操作详情

---

## 六、数据流向与集成

### 6.1 数据流向

```
控制台搜索栏 → 搜索结果匹配 → 点击跳转 → GET /console/lecs-hosts/list → 前端渲染列表页
                                                                                       ↓
LECS主机列表页 → 点击购买按钮 → GET /console/lecs-hosts/create → 前端渲染创建页
                                                                                                   ↓
用户配置各项参数 → 点击立即购买 → POST /api/v1/lecs-hosts → 后端校验 → 创建主机实例 → 返回成功 → 弹窗提示 → 跳转列表页
```

### 6.2 外部依赖

| 依赖项 | 类型 | 用途 | 失败处理 |
|-------|------|------|---------|
| 现有认证系统 | 内部模块 | JWT Token 验证 | 未认证/Token 失效时重定向至登录页 |
| 实例规格数据源 | 内部数据 | 提供实例规格配置信息（vCPU、内存、磁盘、价格） | 加载失败时显示错误提示，禁用提交 |
| 操作系统镜像数据源 | 内部数据 | 提供操作系统镜像列表 | 加载失败时显示错误提示，禁用提交 |
| 配额系统 | 内部模块 | 校验用户可创建的主机数量上限 | 配额校验失败时提示用户 |

---

## 七、成功标准 *(必填)*

### 可衡量指标

- **成功标准 1**: 用户在控制台搜索栏输入"LECS主机"后，可在 1 秒内看到匹配结果并点击跳转
- **成功标准 2**: LECS主机列表页加载完成（包含统计数据和空状态/列表数据）时间不超过 2 秒
- **成功标准 3**: LECS主机创建流程中，用户可在 30 秒内完成所有配置并成功提交创建请求
- **成功标准 4**: 所有可交互组件（按钮、输入框、下拉框、单选框、复选框等）100% 覆盖 `data-testid` 属性
- **成功标准 5**: 列表页和创建页的UI风格与控制台现有页面保持视觉一致性（配色、字体、间距、交互模式）
- **成功标准 6**: 后端 API 接口响应时间 P95 < 500ms

---

## 八、假设与约束

- 假设用户拥有稳定的网络连接，可以正常访问Lee云平台
- v1.0 不支持LECS主机的启动/停止/重启/重置密码等操作，这些功能将在后续版本中提供
- 复用现有的用户认证系统（JWT Cookie），不需要新增认证逻辑
- 实例规格数据（经济型、高性价比型、高性能型）和操作系统镜像数据由后端提供，前端仅负责渲染和选择
- 区域选择暂时固定为"华北-北京四"，后续再扩展多区域支持
- 公网IP的分配和带宽管理由底层基础设施自动处理
- 计费逻辑由后端计算并返回，前端仅做展示
- 创建LECS主机是异步操作，后端创建完成后前端通过轮询或WebSocket通知用户

---

## 九、需求变更与待确认事项

### 待确认项 [NEEDS CLARIFICATION]

> ️ 以下问题需要在进入开发前明确：

1. **LECS主机生命周期管理**: LECS主机创建后是否需要支持启动/停止/重启/删除等完整生命周期管理？v1.0 是否只需要创建功能？
   - **背景**: 列表页截图中包含了开机、关机、重启、重置密码等操作按钮，但需求仅提到创建、删除、查询API
   - **选项 A**: v1.0 仅实现创建和删除，操作按钮先禁用或隐藏 → [减少开发工作量，但用户体验不完整]
   - **选项 B**: v1.0 完整实现列表中的所有操作按钮功能 → [开发工作量较大，但用户体验完整]
   - **选择**: _[等待确认]_

2. **公网IP绑定方式**: 公网访问配置中，弹性公网IP是创建时直接绑定，还是创建后单独创建再绑定？
   - **背景**: 公网访问配置板块中描述了弹性公网IP，但没有明确绑定时机
   - **选项 A**: 创建主机时一并创建并绑定公网IP → [操作更简单，但灵活性较低]
   - **选项 B**: 主机创建后再单独创建公网IP并进行绑定 → [更灵活，但增加了一步操作]
   - **选择**: _[等待确认]_

3. **创建流程交互模式**: LECS主机创建页是一次性填写所有配置并提交，还是分步骤向导式填写？
   - **背景**: 参考截图展示的是长页面包含所有配置板块，但实际可能更适合分步骤
   - **选项 A**: 单页长表单，所有配置在同一页面完成（按截图实现） → [开发简单，与截图一致]
   - **选项 B**: 分步骤向导（步骤1-6），逐步引导用户完成配置 → [用户体验更好，开发工作量较大]
   - **选择**: _[等待确认]_

*注：待确认项最多 3 个，超出部分由需求负责人直接决策*

---

## 附录

### A. 术语表

| 术语 | 定义 |
|-----|------|
| LECS主机 | Lee云平台云服务器（Lee Elastic Cloud Server），用户可创建和管理的虚拟计算实例 |
| 实例规格 | 定义主机的计算资源配置，包括vCPU核数、内存大小、系统盘类型和大小 |
| 实例类型 | 实例规格的分类，包括经济型、高性价比型、高性能型 |
| 镜像 | 操作系统模板，用于创建主机时安装操作系统，如Huawei EulerOS、CentOS、Ubuntu等 |
| 弹性公网IP | 可独立购买和配置的公网IP地址，绑定到LECS主机后可从互联网直接访问 |
| 包年/包月 | 预付费计费模式，用户预先支付一定周期（月或年）的费用 |
| 按需计费 | 后付费计费模式，按实际使用时长计费 |
| 主机安全防护 | 提供风险预防、入侵检测、高级防御等安全防护服务 |

### B. 参考资料

- 项目宪法: `/mnt/d/project_workspace/spec_mode_leecloud/CONSTITUTION.md`
- LECS主机列表页设计稿: `@screanshots/LECS主机/LECS主机-列表.png`
- LECS主机创建-基础配置: `@screanshots/LECS主机/LECS主机-创建-基础配置.png`
- LECS主机创建-实例类型: `@screanshots/LECS主机/LECS主机-创建-实例.png`
- LECS主机创建-操作系统: `@screanshots/LECS主机/LECS主机-创建-操作系统.png`
- LECS主机创建-公网访问: `@screanshots/LECS主机/LECS主机-创建-公网访问.png`
- LECS主机创建-购买量: `@screanshots/LECS主机/LECS主机-创建-购买量.png`
- LECS主机创建-费用与购买: `@screanshots/LECS主机/LECS主机-创建-配置费用与购买.png`
- 现有控制台页面: `specs/006-console-page-with-auth/`

### C. 变更历史

| 版本 | 日期 | 变更内容 | 变更人 |
|-----|------|---------|--------|
| v1.0 | 2026-05-08 | 初始版本，根据用户需求编写 | Sisyphus |

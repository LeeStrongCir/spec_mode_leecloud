# 快速开始：LECS 主机管理

**Date**: 2026-05-09
**Feature**: 007-lecs-hosts

## 前置条件

- Python 3.11+
- 可用的虚拟环境（参见 `backend/README.md`）
- 数据库迁移已更新至最新

## 安装设置

### 1. 进入后端目录

```bash
cd backend
```

### 2. 安装依赖（如果尚未安装）

```bash
uv sync --extra dev
```

### 3. 运行数据库迁移

```bash
uv run alembic upgrade head
```

这将创建 `lecs_hosts` 表，包含迁移中定义的所有列。

### 4. 启动服务器

```bash
uv run uvicorn src.app.main:app --reload --port 8000
```

### 5. 访问页面

- **API 文档**: http://localhost:8000/docs
- **控制台**（搜索 "LECS主机"）: http://localhost:8000/console-full
- **LECS 主机列表页**: http://localhost:8000/console/lecs-hosts/list
- **LECS 主机创建页**: http://localhost:8000/console/lecs-hosts/create

### 6. 通过 API 验证

```bash
# 列出主机（需要有效的 access_token cookie）
curl -b "access_token=<your_token>" http://localhost:8000/api/v1/lecs-hosts

# 创建主机
curl -X POST -b "access_token=<your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "hostname": "test-host-01",
    "billing_mode": "subscription",
    "instance_type": "economy",
    "spec_id": "eco-2c4g",
    "os_image": "huawei_euler",
    "ip_mode": "dhcp",
    "ip_address": null,
    "ip_mask": null,
    "username": "root_admin",
    "password": "MyStr0ng!Pass",
    "duration": 1
  }' \
  http://localhost:8000/api/v1/lecs-hosts

# 获取定价信息
curl -b "access_token=<your_token>" http://localhost:8000/api/v1/lecs-hosts/pricing

# 关闭主机
curl -X POST -b "access_token=<your_token>" \
  http://localhost:8000/api/v1/lecs-hosts/<host_id>/shutdown

# 启动主机
curl -X POST -b "access_token=<your_token>" \
  http://localhost:8000/api/v1/lecs-hosts/<host_id>/start

# 删除主机（必须处于已停止或失败状态）
curl -X DELETE -b "access_token=<your_token>" \
  http://localhost:8000/api/v1/lecs-hosts/<host_id>
```

## 运行测试

```bash
# 单元测试 + 集成测试
cd backend
.venv/bin/python -m pytest tests/test_lecs_host* -v --cov=src/app --cov-report=html
```

## 验证清单

完成设置后，请验证以下事项：

- [ ] 用户可以在控制台搜索栏中搜索 "LECS" 并看到 "LECS主机" 结果
- [ ] 点击搜索结果会导航到 `/console/lecs-hosts/list`
- [ ] 列表页正常加载（新用户显示空表格）
- [ ] 点击 "创建ECS主机" 会导航到创建页面
- [ ] 创建表单会验证 hostname、username、password、IP 输入
- [ ] 选择规格后费用显示实时更新
- [ ] 点击 "立即购买" 会显示包含完整摘要的确认对话框
- [ ] 提交后，新主机出现并显示 "创建中" 状态
- [ ] 约 30 秒后，主机状态变为 "正常"
- [ ] "正常" 状态主机的关机按钮正常工作（状态：关机中 → 已关机）
- [ ] "已关机" 状态主机的开机按钮正常工作（状态：启动中 → 正常）
- [ ] "正常" 状态下删除按钮禁用；"已关机" 状态下启用
- [ ] 软删除的主机从列表中消失
- [ ] 所有交互组件都有 `data-testid` 属性

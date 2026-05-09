# Quickstart: 本地开发环境搭建

**Feature**: 005-login-system  
**Date**: 2026-05-06

## 前置条件

| 工具 | 版本要求 | 安装方式 |
|------|----------|----------|
| Python | 3.11+ | `pyenv` 或系统包管理器 |
| pip | 23.0+ | Python 自带 |
| Git | 2.30+ | 系统包管理器 |
| SQLite | 3.35+ | Python 自带（开发环境） |
| PostgreSQL | 15+ (可选) | Docker 或系统安装（生产模拟） |

## 步骤

### 1. 克隆项目并进入后端目录

```bash
cd backend
```

### 2. 创建虚拟环境

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### 3. 安装项目依赖

```bash
pip install -e ".[dev]"
```

这将安装生产依赖和开发依赖（pytest, pytest-asyncio, pytest-cov, bandit, ruff 等）。

### 4. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`：

```env
# 开发环境
DATABASE_URL=sqlite+aiosqlite:///./dev.db
SECRET_KEY=your-super-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
MAX_FAILED_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=15
```

### 5. 运行数据库迁移

```bash
alembic upgrade head
```

这将创建所有必要的数据库表（User, LoginRecord, Session, AccountLock）。

### 6. 启动开发服务器

```bash
uvicorn src.app.main:app --reload --port 8000
```

访问以下地址：
- API 文档 (Swagger UI): http://localhost:8000/docs
- 登录页面: http://localhost:8000/login
- API 健康检查: http://localhost:8000/health

### 7. 运行测试

```bash
# 全部测试 (Unit + Integration)
pytest

# 带覆盖率报告
pytest --cov=src/app --cov-report=html

# 仅运行单元测试
pytest tests/unit

# 仅运行集成测试
pytest tests/integration

# 运行 E2E 测试
pytest tests/e2e
```

### 8. 运行代码质量检查

```bash
# Linting (ruff)
ruff check src/ tests/

# 格式化 (ruff format)
ruff format src/ tests/

# 安全扫描 (bandit)
bandit -r src/app/
```

## 常见问题

**Q: SQLite 报错 "database is locked"**  
A: 并发写入冲突。开发环境通常不会遇到。如果发生，关闭其他数据库连接后重试。

**Q: JWT 验证失败**  
A: 确保 `SECRET_KEY` 和 `JWT_SECRET_KEY` 在 `.env` 中设置正确。重启服务器后旧令牌失效。

**Q: 测试运行缓慢**  
A: 确保使用 SQLite 内存模式运行测试（conftest.py 配置）。检查是否有多余的数据库连接。

**Q: 迁移失败**  
A: 删除 `dev.db` 后重新运行 `alembic upgrade head`。开发环境允许重置数据库。

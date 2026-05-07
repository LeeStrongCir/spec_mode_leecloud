# Authentication API Contracts

**Feature**: 005-login-system  
**Date**: 2026-05-06

---

## POST /api/auth/login

**Description**: 用户登录认证

**Request Body** (`application/json`):
```json
{
  "identifier": "string",         // 用户名或邮箱
  "password": "string",           // 明文密码
  "remember_me": false            // 是否延长会话有效期
}
```

**Response 200 OK** (登录成功):
```json
{
  "status": "success",
  "message": "登录成功",
  "user": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "username": "zhangsan",
    "email": "zhangsan@example.com"
  }
}
```
- Set-Cookie: `access_token=<JWT>; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=900`
- Set-Cookie: `refresh_token=<JWT>; HttpOnly; Secure; SameSite=Lax; Path=/api/auth/refresh; Max-Age=604800`

**Response 401 Unauthorized** (凭证错误):
```json
{
  "status": "error",
  "error_code": "INVALID_CREDENTIALS",
  "message": "用户名或密码错误"
}
```

**Response 423 Locked** (账号已锁定):
```json
{
  "status": "error",
  "error_code": "ACCOUNT_LOCKED",
  "message": "账号已锁定，请在 15 分钟后重试",
  "unlock_at": "2026-05-06T10:45:00Z"
}
```

**Response 429 Too Many Requests** (速率限制):
```json
{
  "status": "error",
  "error_code": "RATE_LIMITED",
  "message": "登录尝试过于频繁，请稍后再试",
  "retry_after": 60
}
```

**Security Notes**:
- 无论是密码错误还是用户名不存在，返回相同的错误信息（防枚举攻击）(FR-002)
- 密码错误和账号不存在的失败原因在 LoginRecord 中区分为 `wrong_password` 和 `user_not_found` (FR-008)
- 每次登录尝试都产生 LoginRecord (FR-006)
- 登录成功后设置 httpOnly Secure SameSite=Lax Cookie (Decision 2)

---

## POST /api/auth/logout

**Description**: 用户主动登出，撤销当前会话

**Headers**:
- Cookie: `access_token=<jwt>`

**Response 200 OK**:
```json
{
  "status": "success",
  "message": "已登出"
}
```

**Response 401 Unauthorized** (未登录):
```json
{
  "status": "error",
  "error_code": "NOT_AUTHENTICATED",
  "message": "请先登录"
}
```

**Security Notes**:
- 设置 Session.revoked = true (FR-005)
- 清除 Cookie（Max-Age=0）
- 记录登出 LoginRecord

---

## POST /api/auth/refresh

**Description**: 刷新 Access Token

**Headers**:
- Cookie: `refresh_token=<jwt>`

**Request Body**: 无

**Response 200 OK**:
```json
{
  "status": "success",
  "message": "令牌已刷新"
}
```
- Set-Cookie: `access_token=<new_jwt>; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=900`
- Set-Cookie: `refresh_token=<new_jwt>; HttpOnly; Secure; SameSite=Lax; Path=/api/auth/refresh; Max-Age=604800`

**Response 401 Unauthorized** (无效或过期 Refresh Token):
```json
{
  "status": "error",
  "error_code": "INVALID_REFRESH_TOKEN",
  "message": "请重新登录"
}
```

**Security Notes**:
- Refresh Token 每次使用后轮换 (revoke old + issue new) (Decision 2)
- 包含 `typ` 声明防令牌混淆使用
- 包含 `jti` 声明支持撤销

---

## GET /api/auth/me

**Description**: 获取当前登录用户信息

**Headers**:
- Cookie: `access_token=<jwt>`

**Response 200 OK**:
```json
{
  "status": "success",
  "user": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "username": "zhangsan",
    "email": "zhangsan@example.com",
    "last_login_at": "2026-05-06T10:30:00Z",
    "created_at": "2026-01-15T08:00:00Z"
  }
}
```

**Response 401 Unauthorized**:
```json
{
  "status": "error",
  "error_code": "NOT_AUTHENTICATED",
  "message": "请先登录"
}
```

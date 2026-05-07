# Template Context Contracts

## console.html

**Route**: `GET /console`  
**Protection**: Requires authenticated user (`require_auth` dependency)

### Template Context Variables

| Variable | Type | Description | Source |
|----------|------|-------------|--------|
| `request` | `Request` | FastAPI Request object | Injected by route handler |
| `user` | `dict` | JWT payload with `sub` (user ID) and `exp` | From `require_auth` dependency |

### Expected Output

The template renders a full HTML page with:
1. Top navigation bar (Lee Cloud branding, search bar, user controls)
2. Tab bar (总览, 安全监控, 运维监控, 费用与成本)
3. Six dashboard overview cards
4. Service/Resource view panels
5. Four lower dashboard panels (安全监控, 云监控, 费用, 成本)
6. Footer area (欢迎来到Lee云, 产品新特性, 开发者)
7. Right sidebar with action icons
8. Page footer with copyright

---

## login.html (Modified)

**Route**: `GET /login`  
**Protection**: Public (no auth required)

### Template Context Variables

| Variable | Type | Description | Source |
|----------|------|-------------|--------|
| `request` | `Request` | FastAPI Request object | Injected by route handler |
| `error` | `str` (optional) | Error message to display | From `login_page` handler |

### Post-Submit Behavior

On successful login, the handler returns a `RedirectResponse(302)` to `/console` with the JWT cookie set. On failure, the template is re-rendered with `error` set.

---

## login_history.html (Minor Update)

**Route**: `GET /login-history`  
**Protection**: Requires auth

### Template Context Variables

| Variable | Type | Description | Source |
|----------|------|-------------|--------|
| `request` | `Request` | FastAPI Request object | Injected by route handler |
| `user` | `object` | SQLAlchemy User model | From `get_current_user` dependency |
| `records` | `list` | LoginRecord SQLAlchemy models | From `get_login_history` API |

### Branding Changes

All "华为云" references replaced with "Lee云" in page title, header text.

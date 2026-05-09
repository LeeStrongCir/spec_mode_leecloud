# Research: Console Dashboard Implementation

## R1: Login Redirect After Successful Authentication

**Decision**: Use `RedirectResponse` with cookie set directly on the response object.

**Rationale**: The current `POST /api/auth/login` returns JSON (not a redirect). For SSR, the standard pattern is server-side 302 redirect with the JWT cookie set on the `RedirectResponse` directly. This means converting the login endpoint from JSON-response to redirect-response.

**Alternatives considered**:
1. *Client-side redirect via JS* — Requires adding JS to login page; violates the "no JS for auth flow" simplicity principle
2. *Keep JSON response + add a separate JS handler* — More complex; breaks the SSR paradigm
3. *RedirectResponse with cookie on response* — Cleanest, standard for SSR, matches the existing `set_cookie` pattern used in `auth.py`

**Implementation note**: `response.set_cookie()` works on `RedirectResponse`. The status code should be `302` (or `303` for POST-Redirect-GET). Cookie flags remain: `httponly=True`, `samesite="lax"`, `max_age=3600`, `path="/"`.

---

## R2: Console Route Protection Strategy

**Decision**: Use dependency-based `require_auth` with a custom `RedirectToLogin` exception and exception handler.

**Rationale**: Middleware approach would protect ALL routes including API endpoints (which may not want HTML redirects). The dependency approach is more granular — we can decorate specific page routes that need protection while leaving API endpoints on their own auth path.

**Alternatives considered**:
1. *Middleware protecting all routes* — Too broad; would interfere with API endpoints and static files
2. *Dependency with custom exception* — Chosen approach; clean, testable, follows FastAPI patterns
3. *Dependency raising HTTPException 401* — Would return JSON error, not redirect to login page (bad UX for browser users)

**Pattern**:
```python
class RedirectToLogin(Exception):
    def __init__(self, redirect_url: str = "/login"):
        self.redirect_url = redirect_url

async def require_auth(request: Request) -> dict:
    token = request.cookies.get("access_token")
    if not token or not verify_jwt_token(token):
        raise RedirectToLogin(f"/login?next={request.url.path}")
    return verify_jwt_token(token)

@app.exception_handler(RedirectToLogin)
async def redirect_handler(request: Request, exc: RedirectToLogin):
    return RedirectResponse(url=exc.redirect_url, status_code=303)
```

---

## R3: Admin User Seeding Mechanism

**Decision**: Use FastAPI `lifespan` context manager (startup event) with idempotent check.

**Rationale**: Alembic migrations are ideal for production but require storing pre-hashed passwords in migration files (security concern; Argon2id hashes are unique each time). The `lifespan` pattern checks if admin exists before creating, is idempotent across restarts, and allows the password to be hashed at runtime.

**Alternatives considered**:
1. *Alembic migration with raw SQL INSERT + pre-hashed password* — Password hash would be stale; Argon2id hashes are always unique so we cannot embed a known-hash
2. *Alembic migration with raw password + bcrypt/argon2 in SQL* — Not possible without database-specific Argon2id functions
3. *Standalone seed script using SQLAlchemy ORM* — Works but requires manual execution
4. *lifespan startup with idempotent check* — Chosen approach; automatic, idempotent, runtime hashing

**Pattern**:
```python
async with AsyncSession(engine) as session:
    result = await session.execute(select(User).where(User.username == "admin"))
    if not result.scalar_one_or_none():
        admin = User(
            username="admin",
            email="admin@example.com",
            password_hash=hash_password("admin@123"),
            status="active",
        )
        session.add(admin)
        await session.commit()
```

---

## R4: Console Template Structure

**Decision**: Single-file template (`console.html`, ~400 lines) — no `{% include %}` partials.

**Rationale**: The console is a single read-only dashboard page with 5-6 sections, none of which are reused across other templates. A single file is simpler and more maintainable than splitting into partials that have only one consumer.

**Alternatives considered**:
1. *Partials with `{% include %}`* — Over-engineered for a single-consumer dashboard
2. *Single monolithic template* — Chosen approach; matches the simplicity of existing login.html

---

## R5: "华为云" → "Lee云" Replacement Scope

**Decision**: Replace all user-facing instances in templates (4 files) and CSS variable names remain as `hw-*` prefix (not user-facing, low priority).

**Rationale**: The spec (FR-011 through FR-014) requires 100% replacement. The audit found occurrences in:
- `login.html`: title, logo text, login title ("华为账号登录"), disclaimer ("华为账号"), footer copyright ("Huaweicloud.com")
- Additional context files: `login_history.html`, `admin/login_records.html`
- CSS variables like `--hw-red`, `--hw-btn` are prefixed `hw-*` — these are internal identifiers, not user-facing text. Changing them is a risk with no user benefit.

**Not in scope**: CSS CSS variable prefix `hw-*` (internal identifier, not rendered text).

---

## R6: Login Page Form Action (Current Bug Fix)

**Discovery**: The current login page submits a form directly to `/api/auth/login` which returns JSON. The user sees raw JSON on the page with no redirect.

**Decision**: Convert the login endpoint from JSON response to `RedirectResponse`. This aligns with the new console feature requirement and is a pre-existing UX issue.

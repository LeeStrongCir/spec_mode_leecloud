# Data Model: Console Dashboard

## Entities

### User (Admin)

Represents the system administrator account. **No new columns needed** — uses existing User model.

**Existing columns used**:
| Field | Type | Purpose |
|-------|------|---------|
| `id` | UUID | Primary key |
| `username` | String(50) | Admin username ("admin") |
| `email` | String(254) | Admin email |
| `password_hash` | String(255) | Argon2id-hashed password |
| `status` | Enum | "active" |
| `failed_login_count` | SmallInteger | Reset to 0 on login |
| `last_login_at` | DateTime | Updated on login |
| `last_login_ip` | String(45) | Captured on login |
| `created_at` | DateTime | Seeded timestamp |

**Admin identification**: The `username == "admin"` check used in `login_record.py:98` and `deps.py:37` is the admin identifier. No `role` or `is_admin` column needed — admin is identified by the reserved username "admin".

**Seeding**: On server startup (`lifespan`), if no user with `username="admin"` exists, create one with:
- `username="admin"`
- `email="admin@example.com"`
- `password_hash=hash_password("admin@123")` (Argon2id via existing `hash_password` function)
- `status="active"`
- `failed_login_count=0`

### Session (JWT Cookie)

Not a separate entity in data model terms. The authentication state is tracked via:
- **Token**: JWT `access_token` set as httpOnly cookie
- **Payload**: `{"sub": user_id, "exp": expiry}` (existing format, no changes)
- **Verification**: `verify_jwt_token(token)` from `security/` module (existing)

### Dashboard Data (Static/Mock)

The console dashboard displays static placeholder data matching the reference screenshot. No database entities for:
- Security status cards
- Pending payments
- Resource counts
- Cost information
- Service shortcuts

All dashboard content is hard-coded in the Jinja2 template with static text and values. Real data binding is explicitly out of scope per spec Assumptions.

### Key Entities Summary

| Entity | New/Existing | Columns Changed |
|--------|-------------|-----------------|
| User | Existing | None (seeded at startup) |
| Session | Existing | None (JWT cookie, no change) |
| Dashboard Section | N/A | Static template content |
| Service Card | N/A | Static template content |

## Relationships

- **User → LoginRecord**: 1:N (existing, via `login_record.py`)
- **User → Session**: 1:N (existing, via `session.py`)
- **Console Page → User**: N:1 (console requires authenticated user, user data passed as template context)

## State Transitions

- **User lifecycle**: `new` (unverified) → `active` (admin is always "active" after seed)
- **Auth state**: `unauthenticated` → `authenticated` (via login POST + RedirectResponse + cookie set)
- **Login → Console**: `GET /login` → `POST /login` → `302 → GET /console` (redirect flow)

## Validation Rules

- Admin username is reserved: "admin" cannot be registered through user-facing signup
- Admin password must be Argon2id-hashed (uses existing `hash_password` utility)
- JWT token must contain `sub` (user ID) claim for verification

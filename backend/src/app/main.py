from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from app.api.auth import router as auth_router
from app.api.deps import RedirectToLogin, require_auth
from app.api.login_record import router as login_record_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- startup: seed admin user ---
    from sqlalchemy import select
    from app.db import engine, async_session_factory
    from app.models.user import User, UserStatus
    from app.services.password_service import hash_password

    async with async_session_factory() as session:
        result = await session.execute(select(User).where(User.username == "admin"))
        existing_admin = result.scalars().first()
        if existing_admin is None:
            admin = User(
                username="admin",
                email="admin@example.com",
                password_hash=hash_password("admin@123"),
                status=UserStatus.active,
                failed_login_count=0,
            )
            session.add(admin)
            await session.commit()

    yield
    # --- shutdown ---


# --- RedirectToLogin exception handler (SSR auth pages) ---
@app.exception_handler(RedirectToLogin)
async def redirect_handler(request: Request, exc: RedirectToLogin):
    return RedirectResponse(url=exc.redirect_url, status_code=303)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="frontend/templates")
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")


# --- RedirectToLogin exception handler (SSR auth pages) ---
@app.exception_handler(RedirectToLogin)
async def redirect_handler(request: Request, exc: RedirectToLogin):
    return RedirectResponse(url=exc.redirect_url, status_code=303)


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(login_record_router)
app.include_router(auth_router)




@app.get("/console", response_class=HTMLResponse)
async def console_page(request: Request, user=Depends(require_auth)):
    return templates.TemplateResponse(
        request,
        "console.html",
        context={"user": user},
    )


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")


@app.get("/login-history", response_class=HTMLResponse)
async def login_history_page(request: Request):
    return templates.TemplateResponse(
        request,
        "login_history.html",
        context={
            "records": [],
            "pagination": {"total_pages": 0, "page": 1},
        },
    )


@app.get(
    "/admin/login-records", response_class=HTMLResponse
)
async def admin_login_records_page(request: Request):
    return templates.TemplateResponse(
        request,
        "admin/login_records.html",
        context={
            "records": [],
            "pagination": {"total_pages": 0, "page": 1},
            "start_time": "",
            "end_time": "",
            "ip_address": "",
            "status_filter": "all",
        },
    )

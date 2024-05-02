import logging
import secrets

from typing import Annotated
from contextlib import asynccontextmanager

from uvicorn import server
from fastapi import FastAPI, Depends, status, Request
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler
)
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.exceptions import StarletteHTTPException, RequestValidationError, HTTPException
from fastapi_sqlalchemy import DBSessionMiddleware
from starlette.middleware.cors import CORSMiddleware

from app.database import engine
from app.const import const
from app.models import model_user, model_system
from app.routers import (
    router_email,
    router_auth,
    router_admin,
    router_user,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup()
    yield
    await shutdown_event()


# Swagger, Redocly에 접근하는 권한 확인을 위해 환경변수 체크
env = const.ENV

app = FastAPI(
    title="Swit IMAP Server for customers",
    description="IMAP API Server",
    lifespan=lifespan,
    docs_url=None if env == "prod" else "/docs",
    redoc_url=None if env == "prod" else "/redoc"
)

# Swagger-UI에 보안걸기
security = HTTPBasic()


def get_admin(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    correct_username = secrets.compare_digest(credentials.username, const.SWAGGER_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, const.SWAGGER_PASSWORD)
    if not correct_username or not correct_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect Username or Password",
            headers={"WWW-Authenticate": "Basic"}
        )
    return ""


@app.get(path="/docs", include_in_schema=False)
async def get_documentation(admin: str = Depends(get_admin)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Swit IMAP satellite service")


@app.get("/redoc", include_in_schema=False)
async def get_redoc(admin: str = Depends(get_admin)):
    return get_redoc_html(openapi_url="/openapi.json", title="Swit IMAP satellite service")


@app.get(path="/openapi.json", include_in_schema=False)
async def get_openapi(admin: str = Depends(get_admin)):
    return get_openapi(title="Swit IMAP satellite service", version="0.1.0", routes=app.routes)


# Logging 설정
log = logging.getLogger(__name__)


# Generic Error handler
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return await http_exception_handler(request, exc)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print(f"Opps! The client sent invalid data!: {exc}")
    return await request_validation_exception_handler(request, exc)


app.add_middleware(middleware_class=DBSessionMiddleware, db_url=const.DB_URL)

# CORS
origins = ['*']

# Add Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.mount("/static", StaticFiles(directory="static"), name="static")


def include_routers():
    print("Include routers...")
    app.include_router(router_email.router)
    app.include_router(router_auth.router)
    app.include_router(router_admin.router)
    app.include_router(router_user.router)


def init_database():
    print("Initializing database tables...")
    model_user.Base.metadata.create_all(bind=engine)
    model_system.Base.metadata.create_all(bind=engine)


@app.get("/")
async def check_index():
    return {"status": "OK"}


# Startup event
async def startup():
    """
    Startup event
    :return:
    """
    banner = f"""
        ███████╗██╗    ██╗██╗████████╗    ██████╗████████╗███████╗
        ██╔════╝██║    ██║██║╚══██╔══╝   ██╔════╝╚══██╔══╝██╔════╝
        ███████╗██║ █╗ ██║██║   ██║█████╗██║        ██║   ███████╗
        ╚════██║██║███╗██║██║   ██║╚════╝██║        ██║   ╚════██║
        ███████║╚███╔███╔╝██║   ██║      ╚██████╗   ██║   ███████║
        ╚══════╝ ╚══╝╚══╝ ╚═╝   ╚═╝       ╚═════╝   ╚═╝   ╚══════╝
        """
    print(banner)
    print("Swit IMAP Satellite start")

    # Including router
    include_routers()
    # Initialize database tables
    init_database()


async def shutdown_event():
    """
    Shutdown event
    :return:
    """
    goodbye_banner = f"""    
     ██████╗  ██████╗  ██████╗ ██████╗     ██████╗ ██╗   ██╗███████╗██╗
    ██╔════╝ ██╔═══██╗██╔═══██╗██╔══██╗    ██╔══██╗╚██╗ ██╔╝██╔════╝██║
    ██║  ███╗██║   ██║██║   ██║██║  ██║    ██████╔╝ ╚████╔╝ █████╗  ██║
    ██║   ██║██║   ██║██║   ██║██║  ██║    ██╔══██╗  ╚██╔╝  ██╔══╝  ╚═╝
    ╚██████╔╝╚██████╔╝╚██████╔╝██████╔╝    ██████╔╝   ██║   ███████╗██╗
     ╚═════╝  ╚═════╝  ╚═════╝ ╚═════╝     ╚═════╝    ╚═╝   ╚══════╝╚═╝
                                by Swit Customer technical support team
    """
    print(goodbye_banner)
    print("Swit IMAP Satellite shutdown")


if __name__ == "__main__":
    server.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        loop="asyncio",
        reload=True,
        log_level=logging.INFO,
    )

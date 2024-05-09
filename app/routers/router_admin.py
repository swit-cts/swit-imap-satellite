from fastapi import APIRouter, Depends, Body, Query, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from app.services import service_user

router = APIRouter(
    prefix="/admin",
    tags=["Admin Pages"],
    include_in_schema=False
)

templates = Jinja2Templates(directory="templates")

@router.get(
    path="/main",
    response_class=HTMLResponse
)
async def get_admin_main(request: Request):
    return templates.TemplateResponse("/admin/main.html", {"request": request})



@router.get(
    path="/users",
    response_class=HTMLResponse
)
async def get_admin_users(request: Request):
    users = service_user.get_all_users()
    return templates.TemplateResponse("/admin/user_list.html", {"request": request, "users": users})


@router.get(
    path="/env",
    response_class=HTMLResponse
)
async def get_admin_env(request: Request):
    return templates.TemplateResponse("/admin/setting.html", {"request": request})


@router.post(
    path="/user.disable",
)
async def post_admin_user_disable(request: Request):
    user_ids = await request.body()
    user_ids = user_ids.decode("utf-8").split(",")
    service_user.disable_users(user_ids)
    return {"message": "저장 되었습니다."}


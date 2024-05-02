from fastapi import APIRouter, Path, Query

from app.schemas import schema_user
from app.services import service_user

router = APIRouter(prefix="/user")

@router.get("/list")
async def get_user_list():
    return service_user.get_all_users()
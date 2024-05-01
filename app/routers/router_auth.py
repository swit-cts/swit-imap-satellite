from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import StarletteHTTPException

from app.schemas import schema_user
from app.services import service_user

router = APIRouter(
    prefix="/auth",
    tags=["사용자 인증"],
)

@router.post(
    path="/signup",
    summary="사용자 등록",
    response_class=JSONResponse,
)
async def post_auth_signup(param: schema_user.UserAuth):
    """
    사용자 등록
    :param param: 사용자 등록 정보
    :return:
    """
    try:
        # 현재 사용자가 가입되어 있는지 확인한다.
        user = await service_user.get_user(email=param.email)

        if user is not None:
            # 이미 존재하는 사용자일 경우
            raise StarletteHTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="exists")
        else:
            service_user.create_user(param.email, param.password)
            return {"result": "OK"}
    except Exception as e:
        raise StarletteHTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=(e))

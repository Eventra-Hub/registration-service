from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)

from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserUpdate
)

from app.services.user_service import UserService

from app.core.auth import get_current_user
from app.core.security import verify_token


router = APIRouter()

service = UserService()

security = HTTPBearer()


@router.post("/register")
async def register(user: UserCreate):

    return await service.register_user(user)


@router.post("/login")
async def login(user: UserLogin):

    token = await service.login_user(user)

    return {
        "access_token": token
    }


@router.get("/profile/me")
async def get_profile(
    current_user: str = Depends(get_current_user)
):

    return await service.get_profile(current_user)


@router.put("/profile/me")
async def update_profile(
    user: UserUpdate,
    current_user: str = Depends(get_current_user)
):

    return await service.update_profile(
        current_user,
        user
    )


@router.get("/verify")
async def verify_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    payload = verify_token(token)

    if not payload:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    return {
        "user_id": payload.get("sub")
    }

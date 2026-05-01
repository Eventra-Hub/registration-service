from fastapi import APIRouter
from app.schemas.user import UserCreate, UserLogin
from app.services.user_service import UserService

router = APIRouter()
service = UserService()

@router.post("/register")
async def register(user: UserCreate):
    user_id = await service.register_user(user)
    return {"id": user_id}

@router.post("/login")
async def login(user: UserLogin):
    token = await service.login_user(user)
    return {"access_token": token}
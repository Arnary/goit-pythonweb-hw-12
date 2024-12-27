from fastapi import APIRouter, Depends, File, Request, UploadFile
from src.database.db import get_db
from src.services.upload_file import UploadFileService
from src.services.users import UserService
from src.schemas import User
from src.services.auth import get_current_admin_user, get_current_user
from slowapi import Limiter
from slowapi.util import get_remote_address
from src.conf.config import settings
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(prefix="/users", tags=["users"])
limiter = Limiter(key_func=get_remote_address)

@router.get(
    "/me", response_model=User, description="No more than 10 requests per minute"
)
@limiter.limit("10/minute")
async def me(request: Request, user: User = Depends(get_current_user)):
    return user

@router.patch("/avatar", response_model=User, description="For admins only")
async def update_avatar_user(
    file: UploadFile = File(),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    
    if get_current_admin_user(user):
        avatar_url = UploadFileService(
            settings.CLD_NAME, settings.CLD_API_KEY, settings.CLD_API_SECRET
        ).upload_file(file, user.username)

    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.email, avatar_url)

    return user

@router.get("/admin")
def read_admin(current_user: User = Depends(get_current_admin_user)):
    return {"message": f"Вітаємо, {current_user.username}! Це адміністративний маршрут"}

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.schemas import UserCreate

class UserRepository:
    """
    Repository for handling user-related database operations.

    Methods:
    - get_user_by_id(user_id: int) -> User | None: Get a user by ID.
    - get_user_by_username(username: str) -> User | None: Get a user by username.
    - get_user_by_email(email: str) -> User | None: Get a user by email.
    - create_user(body: UserCreate, avatar: str = None) -> User: Create a new user.
    - confirmed_email(email: str) -> None: Confirm email for a user.
    - update_avatar_url(email: str, url: str) -> User: Update user's avatar URL.
    - update_password(email: str, new_password) -> None: Update user's password.
    """
    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_user_by_id(self, user_id: int) -> User | None:
        stmt = select(User).filter_by(id=user_id)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        stmt = select(User).filter_by(username=username)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        stmt = select(User).filter_by(email=email)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def create_user(self, body: UserCreate, avatar: str = None) -> User:
        user = User(
            **body.model_dump(exclude_unset=True, exclude={"password"}),
            hashed_password=body.password,
            avatar=avatar
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def confirmed_email(self, email: str) -> None:
        user = await self.get_user_by_email(email)
        user.confirmed = True
        await self.db.commit()

    async def update_avatar_url(self, email: str, url: str) -> User:
        user = await self.get_user_by_email(email)
        user.avatar = url
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_password(self, email: str, new_password) -> None:
        user = await self.get_user_by_email(email)
        user.hashed_password = new_password
        await self.db.commit()

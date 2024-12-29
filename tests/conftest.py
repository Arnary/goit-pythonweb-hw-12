import asyncio

import pytest
import pytest_asyncio
from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from main import app
from src.database.models import Base, User, Contact
from src.database.db import get_db
from src.services.auth import create_access_token, Hash

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, expire_on_commit=False, bind=engine
)

test_user = {
    "username": "deadpool",
    "email": "deadpool@example.com",
    "password": "12345678",
    "role": "user",
}

test_contact = {
    "first_name": "Alice",
    "last_name": "Black",
    "phone": "1999999999",
    "email": "alice@example.com",
    "birthday": date.today() + timedelta(days=5),
    "additional_info": "Good friend",
}


@pytest.fixture(scope="module", autouse=True)
def init_models_wrap():
    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

        async with TestingSessionLocal() as session:
            hash_password = Hash().get_password_hash(test_user["password"])
            current_user = User(
                username=test_user["username"],
                email=test_user["email"],
                hashed_password=hash_password,
                confirmed=True,
                avatar="https://twitter.com/gravatar",
                role="user",
            )
            current_contact = Contact(
                first_name=test_contact["first_name"],
                last_name=test_contact["last_name"],
                phone=test_contact["phone"],
                email=test_contact["email"],
                birthday=test_contact["birthday"],
                additional_info=test_contact["additional_info"],
                user=current_user,
            )
            session.add(current_user)
            await session.commit()
            await session.refresh(current_user)
            test_user["id"] = current_user.id
            session.add(current_contact)
            await session.commit()

    asyncio.run(init_models())


@pytest.fixture(scope="module")
def client():
    # Dependency override

    async def override_get_db():
        async with TestingSessionLocal() as session:
            try:
                yield session
            except Exception as err:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest_asyncio.fixture()
async def get_token():
    token = await create_access_token(data={"sub": test_user["username"], "id": 1})
    return token

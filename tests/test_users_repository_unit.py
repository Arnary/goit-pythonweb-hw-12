import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas import UserCreate

from src.database.models import Contact, User
from src.repository.users import UserRepository

@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session

@pytest.fixture
def users_repository(mock_session):
    return UserRepository(mock_session)

@pytest.mark.asyncio
async def test_get_user_by_username(users_repository, mock_session):
    # Setup 
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = User(id=1, username="Test", email="testo@gmail.com", avatar="https://example.com/avatar.jpg", role="user")
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    user = await users_repository.get_user_by_username(username="Test")

    # Assertions
    assert user is not None
    assert user.id == 1
    assert user.username == "Test"
    assert user.email == "testo@gmail.com"
    assert user.avatar == "https://example.com/avatar.jpg"
    assert user.role == "user"

@pytest.mark.asyncio
async def test_get_user_by_id(users_repository, mock_session):
    # Setup 
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = User(id=1, username="Test", email="testo@gmail.com", avatar="https://example.com/avatar.jpg", role="user")
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    user = await users_repository.get_user_by_id(user_id=1)

    # Assertions
    assert user is not None
    assert user.id == 1
    assert user.username == "Test"
    assert user.email == "testo@gmail.com"
    assert user.avatar == "https://example.com/avatar.jpg"
    assert user.role == "user"

@pytest.mark.asyncio
async def test_create_user(users_repository):
    # Setup
    user_data = UserCreate(username="Tort", email="tort@gmail.com", password="12345", role="user")

    # Call method
    result = await users_repository.create_user(body=user_data)

    # Assertions
    assert isinstance(result, User)
    assert result.username == "Tort"
    assert result.email == "tort@gmail.com"
    assert result.role == "user"

@pytest.mark.asyncio
async def test_get_user_by_email(users_repository, mock_session):
    # Setup 
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = User(id=1, username="Test", email="testo@gmail.com", avatar="https://example.com/avatar.jpg", role="user")
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    user = await users_repository.get_user_by_email(email="testo@gmail.com")

    # Assertions
    assert user is not None
    assert user.id == 1
    assert user.username == "Test"
    assert user.email == "testo@gmail.com"
    assert user.avatar == "https://example.com/avatar.jpg"
    assert user.role == "user"

@pytest.mark.asyncio
async def test_confirmed_email(users_repository, mock_session):
    # Setup mock
    user_data = User(id=1, username="Test", email="testo@gmail.com", avatar="https://example.com/avatar.jpg", role="user")
    mock_session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=user_data))
    )

    user_data.confirmed = False

    # Run test
    await users_repository.confirmed_email(user_data.email)

    # Assert
    assert user_data.confirmed is True
    mock_session.commit.assert_awaited_once()

@pytest.mark.asyncio
async def test_update_avatar_url(users_repository, mock_session):
    # Setup mock
    user_data = User(id=1, username="Test", email="testo@gmail.com", avatar="https://example.com/avatar.jpg", role="user")
    mock_session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=user_data))
    )
    new_avatar_url = "https://example.com/new_avatar.jpg"

    # Run test
    result = await users_repository.update_avatar_url(user_data.email, new_avatar_url)

    # Assert
    assert result.avatar == new_avatar_url
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)

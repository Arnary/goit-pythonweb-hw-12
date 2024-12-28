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

# @pytest.fixture
# def user():
#     return User(id=1, username="testuser")

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

# @pytest.mark.asyncio
# async def test_update_contact(contacts_repository, mock_session, user):
#     # Setup
#     contact_data = ContactUpdate(id=2, first_name="UpdatedTTT", last_name="T", email="T@example.com", phone="0991111111", birthday="1997-10-20", additional_info="Good person", user=None)
#     existing_contact = Contact(id=2, first_name="TTT", last_name="T", email="T@example.com", phone="0991111111", birthday="2020-10-20", additional_info="", user=None)

#     mock_result = MagicMock()
#     mock_result.scalar_one_or_none.return_value = existing_contact
#     mock_session.execute = AsyncMock(return_value=mock_result)

#     # Call method
#     result = await contacts_repository.update_contact(
#         contact_id=1, body=contact_data, user=user
#     )

#     # Assertions
#     assert result is not None
#     assert result.first_name == "UpdatedTTT"
#     assert result.last_name == "T"
#     assert result.email == "T@example.com"
#     assert result.phone == "0991111111"
#     assert result.birthday == datetime.date(1997, 10, 20)
#     assert result.additional_info == "Good person"
#     mock_session.commit.assert_awaited_once()
#     mock_session.refresh.assert_awaited_once_with(existing_contact)

# @pytest.mark.asyncio
# async def test_remove_contact(contacts_repository, mock_session, user):
#     # Setup
#     existing_contact = ContactBase(id=2, first_name="TTT", last_name="T", email="T@example.com", phone="0991111111", birthday="2020-10-20", additional_info="", user=None)
#     mock_result = MagicMock()
#     mock_result.scalar_one_or_none.return_value = existing_contact
#     mock_session.execute = AsyncMock(return_value=mock_result)

#     # Call method
#     result = await contacts_repository.remove_contact(contact_id=1, user=user)

#     # Assertions
#     assert result is not None
#     assert result.first_name == "TTT"
#     assert result.last_name == "T"
#     assert result.email == "T@example.com"
#     assert result.phone == "0991111111"
#     assert result.birthday == datetime.date(2020, 10, 20)
#     assert result.additional_info == ""
#     mock_session.delete.assert_awaited_once_with(existing_contact)
#     mock_session.commit.assert_awaited_once()

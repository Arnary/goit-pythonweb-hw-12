import datetime
import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas import ContactBase, ContactUpdate

from src.database.models import Contact, User
from src.repository.contacts import ContactRepository

@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session

@pytest.fixture
def contacts_repository(mock_session):
    return ContactRepository(mock_session)

@pytest.fixture
def user():
    return User(id=1, username="testuser")

@pytest.mark.asyncio
async def test_get_contacts(contacts_repository, mock_session, user):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        Contact(id=1, first_name="Test", last_name="Testov", email="test@example.com", phone="0999999999", birthday="2024-12-28", additional_info="", user=user)
    ]
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    contacts = await contacts_repository.get_contacts(skip=0, limit=10, query=None, user=user)

    # Assertions
    assert len(contacts) == 1
    assert contacts[0].first_name == "Test"
    assert contacts[0].last_name == "Testov"
    assert contacts[0].email == "test@example.com"
    assert contacts[0].phone == "0999999999"
    assert contacts[0].birthday == "2024-12-28"
    assert contacts[0].additional_info == ""


@pytest.mark.asyncio
async def test_get_contact_by_id(contacts_repository, mock_session, user):
    # Setup 
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = Contact(id=1, first_name="Test", last_name="Testov", email="test@example.com", phone="0999999999", birthday="2024-12-28", additional_info="", user=user)
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    contact = await contacts_repository.get_contact_by_id(contact_id=1, user=user)

    # Assertions
    assert contact is not None
    assert contact.id == 1
    assert contact.first_name == "Test"
    assert contact.last_name == "Testov"
    assert contact.email == "test@example.com"
    assert contact.phone == "0999999999"
    assert contact.birthday == "2024-12-28"
    assert contact.additional_info == ""

@pytest.mark.asyncio
async def test_create_contact(contacts_repository, mock_session, user):
    # Setup
    contact_data = ContactBase(id=2, first_name="TTT", last_name="T", email="T@example.com", phone="0991111111", birthday="2020-10-20", additional_info="", user=None)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = Contact(
        id=1, first_name=contact_data.first_name, last_name=contact_data.last_name, email=contact_data.email,phone=contact_data.phone, birthday=contact_data.birthday, additional_info=contact_data.additional_info, user=user
    )
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await contacts_repository.create_contact(body=contact_data, user=user)

    # Assertions
    assert isinstance(result, Contact)
    assert result.first_name == "TTT"
    assert result.last_name == "T"
    assert result.email == "T@example.com"
    assert result.phone == "0991111111"
    assert result.birthday == datetime.date(2020, 10, 20)
    assert result.additional_info == ""

@pytest.mark.asyncio
async def test_update_contact(contacts_repository, mock_session, user):
    # Setup
    contact_data = ContactUpdate(id=2, first_name="UpdatedTTT", last_name="T", email="T@example.com", phone="0991111111", birthday="1997-10-20", additional_info="Good person", user=None)
    existing_contact = Contact(id=2, first_name="TTT", last_name="T", email="T@example.com", phone="0991111111", birthday="2020-10-20", additional_info="", user=None)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await contacts_repository.update_contact(
        contact_id=1, body=contact_data, user=user
    )

    # Assertions
    assert result is not None
    assert result.first_name == "UpdatedTTT"
    assert result.last_name == "T"
    assert result.email == "T@example.com"
    assert result.phone == "0991111111"
    assert result.birthday == datetime.date(1997, 10, 20)
    assert result.additional_info == "Good person"
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(existing_contact)

@pytest.mark.asyncio
async def test_remove_contact(contacts_repository, mock_session, user):
    # Setup
    existing_contact = ContactBase(id=2, first_name="TTT", last_name="T", email="T@example.com", phone="0991111111", birthday="2020-10-20", additional_info="", user=None)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await contacts_repository.remove_contact(contact_id=1, user=user)

    # Assertions
    assert result is not None
    assert result.first_name == "TTT"
    assert result.last_name == "T"
    assert result.email == "T@example.com"
    assert result.phone == "0991111111"
    assert result.birthday == datetime.date(2020, 10, 20)
    assert result.additional_info == ""
    mock_session.delete.assert_awaited_once_with(existing_contact)
    mock_session.commit.assert_awaited_once()

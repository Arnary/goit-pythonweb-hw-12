import pytest
from datetime import datetime, date
from pydantic import ValidationError
from src.database.models import UserRole
from src.schemas import (
    ContactBase,
    ContactResponse,
    User,
    UserCreate,
    Token,
    RequestEmail
)


def test_contact_base_valid():
    contact = ContactBase(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="123456789",
        birthday=date(1990, 1, 1),
        additional_info="Some info"
    )
    assert contact.first_name == "John"
    assert contact.email == "john.doe@example.com"

def test_contact_response_valid():
    contact_response = ContactResponse(
        id=1,
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="123456789",
        birthday=date(1990, 1, 1),
        additional_info="Some info",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    assert contact_response.id == 1

def test_user_valid():
    user = User(
        id=1,
        username="johndoe",
        email="john.doe@example.com",
        avatar="https://example.com/avatar.png",
        role=UserRole.USER
    )
    assert user.username == "johndoe"

def test_user_create_valid():
    user_create = UserCreate(
        username="johndoe",
        email="john.doe@example.com",
        password="securepassword",
        role=UserRole.USER
    )
    assert user_create.email == "john.doe@example.com"

def test_token_valid():
    token = Token(access_token="token123", token_type="bearer")
    assert token.access_token == "token123"

def test_request_email_valid():
    request_email = RequestEmail(email="john.doe@example.com")
    assert request_email.email == "john.doe@example.com"

def test_request_email_invalid():
    with pytest.raises(ValidationError):
        RequestEmail(email="invalid-email")

from unittest.mock import Mock, AsyncMock, patch

import pytest
from sqlalchemy import select

from tests.conftest import TestingSessionLocal
from src.database.models import User
from src.services.auth import create_email_token


user_data = {
    "username": "agent007",
    "email": "agent007@gmail.com",
    "password": "12345678",
    "role": "user",
}


def test_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "hashed_password" not in data
    assert "avatar" in data

def test_repeat_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "Користувач з таким email вже існує"

def test_not_confirmed_login(client):
    response = client.post(
        "api/auth/login",
        data={
            "username": user_data.get("username"),
            "password": user_data.get("password"),
        },
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Електронна адреса не підтверджена"

@pytest.mark.asyncio
async def test_login(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(select(User).where(User.email == user_data.get("email")))
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = True
            await session.commit()

    response = client.post("api/auth/login",
                           data={"username": user_data.get("username"), "password": user_data.get("password")})
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data

def test_wrong_password_login(client):
    response = client.post(
        "api/auth/login",
        data={"username": user_data.get("username"), "password": "password"},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Неправильний логін або пароль"

def test_wrong_username_login(client):
    response = client.post(
        "api/auth/login",
        data={"username": "username", "password": user_data.get("password")},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Неправильний логін або пароль"

def test_validation_error_login(client):
    response = client.post(
        "api/auth/login", data={"password": user_data.get("password")}
    )
    assert response.status_code == 422, response.text
    data = response.json()
    assert "detail" in data

def test_confirmed_email_fail(client):
    token = "non valid token"
    response = client.get(f"api/auth/confirmed_email/{token}")
    assert response.status_code == 422
    data = response.json()
    assert data["detail"] == "Неправильний токен для перевірки електронної пошти"

def test_confirmed_email_confirmed(client, monkeypatch):
    async def mock_get_user_by_email(self, email):
        user_data_copy = user_data.copy()
        user_data_copy.pop("password")
        user = User(**user_data_copy)
        user.confirmed = False
        return user

    monkeypatch.setattr(
        "src.services.users.UserService.get_user_by_email", mock_get_user_by_email
    )

    token = create_email_token({"sub": user_data["email"]})
    response = client.get(f"api/auth/confirmed_email/{token}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Електронну пошту підтверджено"

def test_confirmed_email_already_confirmed(client):
    token = create_email_token({"sub": user_data["email"]})
    response = client.get(f"api/auth/confirmed_email/{token}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Ваша електронна пошта вже підтверджена"

def test_request_email(client, monkeypatch):
    async def mock_get_user_by_email(self, email):
        user_data_copy = user_data.copy()
        user_data_copy.pop("password")
        user = User(**user_data_copy)
        user.confirmed = False
        return user

    monkeypatch.setattr(
        "src.services.users.UserService.get_user_by_email", mock_get_user_by_email
    )
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post("api/auth/request_email", json={"email": user_data["email"]})
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Перевірте свою електронну пошту для підтвердження"

@pytest.mark.asyncio
async def test_reset_password(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)

    body = {"email": user_data.get("email")}
    response = client.post("api/auth/request_password_reset", json=body)

    assert response.status_code == 200, response.text
    assert response.json() == {
        "message": "Лист для скидання пароля надіслано на вашу електронну адресу"
    }
    mock_send_email.assert_called_once()

@pytest.mark.asyncio
async def test_reset_password_not_confirmed(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)

    body = {"email": "nonexistent@example.com"}
    response = client.post("api/auth/request_password_reset", json=body)

    assert response.status_code == 404
    assert response.json() == {"detail": "Користувач не знайдений"}
    mock_send_email.assert_not_called()

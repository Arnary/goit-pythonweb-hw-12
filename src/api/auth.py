from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
import jsonpickle
import redis
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from src.schemas import UserCreate, Token, User, RequestEmail
from src.services.auth import create_access_token, Hash, get_email_from_token
from src.services.users import UserService
from src.database.db import get_db
from src.services.email import send_email


router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate, 
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
    ):
    """
    Register a new user.

    Args:
        user_data (UserCreate): User data to register.
        background_tasks (BackgroundTasks): Background tasks to be executed.
        request (Request): Request object.
        db (Session, optional): Database session. Defaults to Depends(get_db).

    Returns:
        User: The newly registered user.
    """
    user_service = UserService(db)

    email_user = await user_service.get_user_by_email(user_data.email)
    if email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Користувач з таким email вже існує",
        )

    username_user = await user_service.get_user_by_username(user_data.username)
    if username_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Користувач з таким іменем вже існує",
        )
    user_data.password = Hash().get_password_hash(user_data.password)
    new_user = await user_service.create_user(user_data)
    background_tasks.add_task(
    send_email, new_user.email, new_user.username, request.base_url, "verify_email"
    )

    return new_user

@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Login a user.

    Args:
        form_data (OAuth2PasswordRequestForm, optional): Form data for login. Defaults to Depends().
        db (Session, optional): Database session. Defaults to Depends(get_db).

    Returns:
        Token: The access token for the logged-in user.
    """
    r = redis.Redis(host='localhost', port=6379, db=0)
    user_service = UserService(db)
    user = await user_service.get_user_by_username(form_data.username)
    if not user or not Hash().verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильний логін або пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Електронна адреса не підтверджена",
        )

    r.set(str(user.username), jsonpickle.encode(user))
    r.expire(str(user.username), 3600)

    access_token = await create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    Confirm email for a user.

    Args:
        token (str): Verification token.
        db (Session, optional): Database session. Defaults to Depends(get_db).

    Returns:
        dict: Message confirming email confirmation.
    """
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Ваша електронна пошта вже підтверджена"}
    await user_service.confirmed_email(email)
    return {"message": "Електронну пошту підтверджено"}

@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Request email verification.

    Args:
        body (RequestEmail): Email request data.
        background_tasks (BackgroundTasks): Background tasks to be executed.
        request (Request): Request object.
        db (Session, optional): Database session. Defaults to Depends(get_db).

    Returns:
        dict: Message confirming email verification request.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user.confirmed:
        return {"message": "Ваша електронна пошта вже підтверджена"}
    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url, "verify_email"
        )
    return {"message": "Перевірте свою електронну пошту для підтвердження"}


@router.post("/request_password_reset")
async def request_password_reset(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Request a password reset.

    Args:
        body (RequestEmail): Email request data.
        background_tasks (BackgroundTasks): Background tasks to be executed.
        request (Request): Request object.
        db (Session, optional): Database session. Defaults to Depends(get_db).

    Returns:
        dict: Message indicating password reset email has been sent.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Користувач не знайдений"
        )

    background_tasks.add_task(
        send_email, user.email, user.username, request.base_url, "reset_password"
    )

    return {"message": "Лист для скидання пароля надіслано на вашу електронну адресу"}


@router.post("/reset-password-confirm/{token}")
async def reset_password_confirm(
    token: str,
    new_password: str,
    db: Session = Depends(get_db),
):
    """
    Confirm password reset.

    Args:
        token (str): Reset token.
        new_password (str): New password.
        db (Session, optional): Database session. Defaults to Depends(get_db).

    Returns:
        dict: Message confirming password reset.
    """
    try:
        email = await get_email_from_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Токен недійсний або прострочений",
        )

    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Користувач не знайдений"
        )

    hashed_password = Hash().get_password_hash(new_password)
    await user_service.update_password(email, hashed_password)

    return {"message": "Пароль успішно оновлено"}

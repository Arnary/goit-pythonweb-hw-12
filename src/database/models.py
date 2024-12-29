from datetime import datetime
from enum import Enum

from sqlalchemy import Integer, String, func, Column, ForeignKey, Boolean, Enum as SqlEnum
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase, relationship
from sqlalchemy.sql.sqltypes import DateTime, Date
from datetime import datetime, date


class Base(DeclarativeBase):
    """
    Base class for declarative base.

    This class can be used as a base for SQLAlchemy declarative classes.
    """
    pass


class UserRole(str, Enum):
    """
    Enum class for user roles.

    Attributes:
    - USER: User role.
    - ADMIN: Admin role.
    """
    USER = "user"
    ADMIN = "admin"


class Contact(Base):
    """
    Contact model representing contact information.

    Attributes:
    - id (int): Contact ID.
    - first_name (str): First name of the contact.
    - last_name (str): Last name of the contact.
    - email (str): Email address of the contact.
    - phone (str): Phone number of the contact.
    - birthday (date): Birthday of the contact.
    - additional_info (str): Additional information about the contact.
    - created_at (datetime): Creation timestamp of the contact.
    - updated_at (datetime): Last updated timestamp of the contact.
    - user_id: ID of the associated user.
    - user: Relationship to the User model.
    """
    __tablename__ = "contacts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=False)
    birthday: Mapped[date] = mapped_column(Date)
    additional_info: Mapped[str] = mapped_column(String(250), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        "created_at", DateTime, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        "updated_at", DateTime, default=func.now(), onupdate=func.now()
    )

    user_id = Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), default=None)
    user = relationship("User", backref="notes")


class User(Base):
    """
    User model representing user information.

    Attributes:
    - id (int): User ID.
    - username (str): Username of the user.
    - email (str): Email address of the user.
    - hashed_password (str): Hashed password of the user.
    - created_at (datetime): Creation timestamp of the user.
    - avatar (str): Avatar URL of the user.
    - confirmed (bool): Confirmation status of the user.
    - role (UserRole): Role of the user.
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
    role = Column(SqlEnum(UserRole), default=UserRole.USER, nullable=False)

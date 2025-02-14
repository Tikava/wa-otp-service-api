from typing import List
import enum

from sqlalchemy import String, ForeignKey, BigInteger, Enum, Boolean, DateTime, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship
)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(), server_default=func.now())

    businesses: Mapped[List["Business"]] = relationship(
        back_populates="admin", cascade="all, delete-orphan"
    )


class Business(Base):
    __tablename__ = "businesses"

    id: Mapped[int] = mapped_column(primary_key=True)
    admin_id: Mapped[int] = mapped_column(ForeignKey("admins.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    whatsapp_api_token: Mapped[str] = mapped_column(String(255), nullable=False)
    phone_number_id: Mapped[str] = mapped_column(String(), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(), server_default=func.now())

    admin: Mapped["Admin"] = relationship(back_populates="businesses")
    clients: Mapped[List["Client"]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id", ondelete="CASCADE"))
    scopes: Mapped[str] = mapped_column(String(255))
    api_key: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(), server_default=func.now())

    business: Mapped["Business"] = relationship(back_populates="clients")
    otps: Mapped[List["OTP"]] = relationship(
        back_populates="client", cascade="all, delete-orphan"
    )


class UserStatus(enum.Enum):
    VERIFIED = "VERIFIED"
    NOT_VERIFIED = "NOT_VERIFIED"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    phone_number: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    status: Mapped[UserStatus] = mapped_column(Enum(UserStatus, name="user_status"), server_default=UserStatus.NOT_VERIFIED.name)
    created_at: Mapped[DateTime] = mapped_column(DateTime(), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(), nullable=True, server_onupdate=func.now())

    otps: Mapped[List["OTP"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class OTP(Base):
    __tablename__ = "otps"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id", ondelete="CASCADE"))
    otp_code: Mapped[str] = mapped_column(String(10), index=True, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(), server_default=func.now())
    expires_at: Mapped[DateTime] = mapped_column(DateTime(), nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean(), default=False, index=True)

    user: Mapped["User"] = relationship(back_populates="otps")
    client: Mapped["Client"] = relationship(back_populates="otps")
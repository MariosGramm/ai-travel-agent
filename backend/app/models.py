import uuid
from datetime import datetime, timezone

from pydantic import EmailStr
from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel
from typing import List, Optional


# -----------------------------------------------------------------------------
# SQLModel notes
# -----------------------------------------------------------------------------
# In this file we use SQLModel classes in two different ways:
#
# 1. Database models
#    Classes declared with `table=True`, for example `class User(..., table=True)`,
#    are mapped to real database tables. Their fields become table columns and
#    their `Relationship(...)` attributes describe ORM relationships.
#
# 2. Schemas / DTOs
#    Classes without `table=True` are not database tables. They are Pydantic-style
#    schemas used for request validation and response serialization in the API.
#    Typical examples are `UserCreate`, `UserUpdate`, `UserPublic`, etc.
#
# Common naming convention used below:
# - Base   : shared fields reused by both models and schemas.
# - Create : fields accepted when creating a resource through the API.
# - Update : fields accepted when updating a resource through the API.
# - Public : fields returned to the client through the API.
# - PluralPublic : wrapper schema for list responses, usually with data + count.
# -----------------------------------------------------------------------------


def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)


# -----------------------------------------------------------------------------
# User schemas and model
# -----------------------------------------------------------------------------


# Base schema: shared user fields used by API schemas and the DB model.
# This is not a DB table because it does not use `table=True`.
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    first_name: str | None = Field(default=None, max_length=255)
    last_name: str | None = Field(default=None, max_length=255)


# API schema: data received when an admin/system creates a user.
# It extends UserBase and adds the plain password received from the client.
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


# API schema: data received when a user registers.
# It is separated from UserCreate so registration can expose only the fields
# that a normal user is allowed to submit.
class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    first_name: str | None = Field(default=None, max_length=255)
    last_name: str | None = Field(default=None, max_length=255)

# API schema: data received when updating a user.
# All fields are optional because PATCH/partial-update endpoints should allow
# the client to send only the fields that need to change.
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore[assignment]
    password: str | None = Field(default=None, min_length=8, max_length=128)


# API schema: fields a logged-in user can update for their own account.
class UserUpdateMe(SQLModel):
    first_name: str | None = Field(default=None, max_length=255)
    last_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


# API schema: payload used for changing an existing password.
class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


# Database model: this class maps to the `user` table because of `table=True`.
# It contains database-only fields such as `id`, `hashed_password`, timestamps,
# and ORM relationships. Notice that we store `hashed_password`, not the plain
# password received by UserCreate/UserRegister
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    updated_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
        sa_column_kwargs={"default": get_datetime_utc, "onupdate": get_datetime_utc},
    )


# API response schema: public representation of a user.
# It intentionally excludes sensitive/internal fields such as `hashed_password`.
class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime | None = None
    updated_at: datetime | None = None


# API response schema: standard list response for users.
class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int
import uuid

from sqlmodel import SQLModel, Field
from pydantic import EmailStr
from datetime import datetime, UTC

# Shared Model
class UserBase(SQLModel):
    """
    Base model for user-related data.
    """ 
    first_name: str = Field(max_length=50, description="The first name of the user.")
    last_name: str = Field(max_length=50, description="The last name of the user.")
    email : EmailStr = Field(max_length=100, description="The email address of the user.")
    is_active: bool = Field(default=True, description="Indicates whether the user is active.")
    is_superuser: bool = Field(default=False, description="Indicates whether the user has superuser privileges.")

# User creation DTOs
class UserCreateDTO(UserBase):
    """
    Model for creating a new user.
    Used ONLY by the superuser to create a new user.
    Inherits from UserBase and adds a password field.
    """
    password: str = Field(min_length=8, description="The password for the user account.")

class UserCreateSignupDTO(SQLModel):
    """
    Used by the user to sign up.
    Model for user signup.
    """
    first_name: str = Field(max_length=50, description="The first name of the user.")
    last_name: str = Field(max_length=50, description="The last name of the user.")
    email : EmailStr = Field(max_length=100, description="The email address of the user.")
    password: str = Field(min_length=8, description="The password for the user account.")


    
# User update DTOs
class UserUpdateDTO(SQLModel):
    """
    Model for updating user information.
    Used ONLY by the superuser to update user information.
    All fields are optional to allow partial updates.
    """

    email: EmailStr | None = Field(default=None, max_length=100, description="The email address of the user.")
    first_name: str | None = Field(default=None, max_length=50, description="The first name of the user.")
    last_name: str | None = Field(default=None, max_length=50, description="The last name of the user.")
    password: str | None = Field(default=None, min_length=8, description="The password for the user account.")
    is_active: bool | None = Field(default=None, description="Indicates whether the user is active.")
    is_superuser: bool | None = Field(default=None, description="Indicates whether the user has superuser privileges.")


class UserUpdateSelfDTO(SQLModel):
    """
    Model for updating user information by the user themselves.
    All fields are optional to allow partial updates.
    """
    first_name: str | None = Field(default=None, max_length=50, description="The first name of the user.")
    last_name: str | None = Field(default=None, max_length=50, description="The last name of the user.")
    password: str | None = Field(default=None, min_length=8, description="The password for the user account.")
    email: EmailStr | None = Field(default=None, max_length=100, description="The email address of the user.")

class UserUpdatePasswordDTO(SQLModel):
    """
    Model for updating user password.
    All fields are required to ensure proper password update.
    """
    current_password: str = Field(min_length=8, description="The current password of the user.")
    new_password: str = Field(min_length=8, description="The new password for the user account.")

# User model
class User(UserBase, table=True):
    """
    Database model for the User.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="The unique identifier for the user.")
    hashed_password: str = Field(max_length=255, description="The hashed password for the user account.")
    created_at: datetime | None = Field(
        default_factory= datetime.now(UTC), 
        sa_type=DateTime(timezone=True),  # type: ignore
    )


from sqlmodel import SQLModel, Field
from pydantic import EmailStr

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

# User creation models

class UserCreate(UserBase):
    """
    Used ONLY by the superuser to create a new user.
    Model for creating a new user.
    Inherits from UserBase and adds a password field.
    """
    password: str = Field(min_length=8, description="The password for the user account.")

class UserCreateSignup(SQLModel):
    """
    Used by the user to sign up.
    Model for user signup.
    """
    first_name: str = Field(max_length=50, description="The first name of the user.")
    last_name: str = Field(max_length=50, description="The last name of the user.")
    email : EmailStr = Field(max_length=100, description="The email address of the user.")
    password: str = Field(min_length=8, description="The password for the user account.")
    






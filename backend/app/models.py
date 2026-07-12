import uuid
from typing import List
from app.enums import ChatRole
from sqlmodel import Relationship, SQLModel, Field
from pydantic import EmailStr
from datetime import datetime, UTC

# Shared Models
class UserBase(SQLModel):
    """
    Base model for user-related data.
    """ 
    first_name: str = Field(max_length=50, description="The first name of the user.")
    last_name: str = Field(max_length=50, description="The last name of the user.")
    email : EmailStr = Field(max_length=100, description="The email address of the user.")
    is_active: bool = Field(default=True, description="Indicates whether the user is active.")
    is_superuser: bool = Field(default=False, description="Indicates whether the user has superuser privileges.")

class AuditableBase(SQLModel):
    """
    Base model for auditable entities.
    """
    created_at: datetime | None = Field(
        default_factory= lambda: datetime.now(UTC), 
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    updated_at: datetime | None = Field(
        default_factory= lambda: datetime.now(UTC),
        sa_type=DateTime(timezone=True),  # type: ignore
    )

#=======================================================================================================
# USER MODELS
#=======================================================================================================

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

# User entity model
class User(UserBase, AuditableBase, table=True):
    """
    Database entity for the User.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="The unique identifier for the user.")
    hashed_password: str = Field(max_length=255, description="The hashed password for the user account.")

    chat_sessions: List["ChatSession"] = Field(Relationship(back_populates="owner"), description="A list of chat sessions associated with the user.")

    #TODO : Add relationships to other models if needed in the future.

# Public user models for API responses
class UserPublic(UserBase):
    """
    Public representation of the User model.
    Used for API responses to avoid exposing sensitive information.
    """
    id: uuid.UUID = Field(description="The unique identifier for the user.")
    created_at: datetime | None = Field(description="The timestamp when the user was created.")

class UsersPublic(SQLModel):
    """
    Model for a list of public user representations.
    Used for API responses when returning multiple users.
    """
    users: list[UserPublic] = Field(description="A list of public user representations.")
    count: int = Field(description="The total number of users returned.")

#=======================================================================================================
# CHAT MODELS
#=======================================================================================================

#Chat session entity model 
class ChatSession(SQLModel, AuditableBase, table=True):
    """
    Database entity for the ChatSession.
    Represents a chat session between a user and the AI travel agent.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="The unique identifier for the chat session.")
    owner_id: uuid.UUID = Field(foreign_key="user.id", description="The unique identifier of the user associated with this chat session.")
    memory: List[str] = Field(default=[], description="A list of messages exchanged in the chat session.")

    owner: "User" = Field(Relationship(back_populates="chat_sessions"), description="The user associated with this chat session.")

#Chat message entity model
class ChatMessage(SQLModel, AuditableBase, table=True):
    """
    Database entity for the ChatMessage.
    Represents a single message in a chat session.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="The unique identifier for the chat message.")
    chat_session_id: uuid.UUID = Field(foreign_key="chatsession.id", description="The unique identifier of the chat session associated with this message.")
    role : ChatRole = Field(description="The role of the participant who sent the message (user or assistant).")    #user or assistant
    content: str = Field(description="The content of the chat message.")
    created_at: datetime | None = Field(
        default_factory= lambda: datetime.now(UTC), 
        sa_type=DateTime(timezone=True),  # type: ignore
    )


        

import uuid
from app.enums import AccommodationType, ActivityType, AgentStep, ChatRole, Currency, PartOfDay, SearchSessionStatus, TravelPackageTier
from sqlmodel import ARRAY, Column, DateTime, Relationship, SQLModel, Field, String
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

    chat_sessions: list["ChatSession"] = Field(Relationship(back_populates="owner"), description="A list of chat sessions associated with the user.")
    search_sessions: list["SearchSession"] = Field(Relationship(back_populates="owner"), description="A list of search sessions associated with the user.")

# Public user DTOs for API responses
class UserPublicDTO(UserBase):
    """
    Public representation of the User model.
    Used for API responses to avoid exposing sensitive information.
    """
    id: uuid.UUID = Field(description="The unique identifier for the user.")
    created_at: datetime | None = Field(description="The timestamp when the user was created.")

class UsersPublicDTO(SQLModel):
    """
    Model for a list of public user representations.
    Used for API responses when returning multiple users.
    """
    users: list[UserPublicDTO] = Field(description="A list of public user representations.")
    count: int = Field(description="The total number of users returned.")

#=======================================================================================================
# CHAT MODELS
#=======================================================================================================

# Chat session entity model 
class ChatSession(SQLModel, AuditableBase, table=True):
    """
    Database entity for the ChatSession.
    Represents a chat session between a user and the AI travel agent.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="The unique identifier for the chat session.")
    owner_id: uuid.UUID = Field(foreign_key="user.id", description="The unique identifier of the user associated with this chat session.")

    owner: "User" = Field(Relationship(back_populates="chat_sessions"), description="The user associated with this chat session.")
    messages : list["ChatMessage"] = Relationship(back_populates="session")

# Chat message entity model
class ChatMessage(SQLModel, AuditableBase, table=True):
    """
    Database entity for the ChatMessage.
    Represents a single message in a chat session.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="The unique identifier for the chat message.")
    chat_session_id: uuid.UUID = Field(foreign_key="chatsession.id", description="The unique identifier of the chat session associated with this message.")
    role : ChatRole = Field(description="The role of the participant who sent the message (user or assistant).")    
    content: str = Field(description="The content of the chat message.")
    created_at: datetime | None = Field(
        default_factory= lambda: datetime.now(UTC), 
        sa_type=DateTime(timezone=True),  # type: ignore
    )

    session: "ChatSession" = Relationship(back_populates="messages")

#=======================================================================================================
# SEARCH MODELS
#=======================================================================================================

# Search session entity model
class SearchSession(SQLModel, AuditableBase, table=True):
    """
    Database entity for the SearchSession.
    Represents a search session initiated by a user.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="The unique identifier for the search session.")
    owner_id: uuid.UUID = Field(foreign_key="user.id", description="The unique identifier of the user associated with this search session.")
    destination: str = Field(max_length=200, description="The travel destination for the search session.")
    date_from: datetime = Field(description="The start date for the travel search.")
    date_to: datetime = Field(description="The end date for the travel search.")
    budget: float = Field(description="The budget for the travel search.")
    currency: Currency = Field(default=Currency.EUR, description="The currency code for the budget (e.g., USD, EUR).")
    status: SearchSessionStatus = Field(default=SearchSessionStatus.PENDING, description="The status of the search session (pending, completed, or failed).")
    error_message: str | None = Field(default=None, description="An optional error message if the search session failed.")

    owner: "User" = Field(Relationship(back_populates="search_sessions"), description="The user associated with this search session.")
    search_history: list["SearchHistory"] = Field(Relationship(back_populates="session"), description="A list of search history records associated with this search session.")
    travel_packages: list["TravelPackage"] = Field(Relationship(back_populates="session"), description="A list of travel packages that were generated in the current search session")

# Search history entity model
class SearchHistory(SQLModel, table=True):
    """
    Database entity for the SearchHistory.
    Represents a record of a completed search session.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="The unique identifier for the search history record.")
    search_session_id: uuid.UUID = Field(foreign_key="searchsession.id", description="The unique identifier of the search session associated with this history record.")
    step: AgentStep = Field(description="The step of the AI travel agent's process that this history record corresponds to.")
    input: str = Field(description="The input data for the corresponding step of the AI travel agent's process.")          
    output: str = Field(description="The output data for the corresponding step of the AI travel agent's process.")        
    duration_ms: int = Field(description="The duration in milliseconds for the corresponding step of the AI travel agent's process.")
    created_at: datetime | None = Field(
        default_factory= lambda: datetime.now(UTC), 
        sa_type=DateTime(timezone=True),  # type: ignore
    )

    session: "SearchSession" = Field(Relationship(back_populates="search_history"), description="The search session associated with this history record.")

#=======================================================================================================
# TRAVEL MODELS (Search results)
#=======================================================================================================

# Travel package entity model
class TravelPackage(SQLModel, table=True):
    """
    Database entity for the TravelPackage.
    Represents a travel package as a search result.
    """
    id : uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="The unique identifier for the travel package.")
    session_id: uuid.UUID = Field(foreign_key="searchsession.id", description="The unique identifier of the search session associated with this travel package.")

    tier : TravelPackageTier = Field(description="The tier of the travel package (budget, standard, or luxury).")
    estimated_cost_min: float = Field(description="The minimum estimated cost of the travel package")
    estimated_cost_max: float = Field(description="The maximum estimated cost of the travel package")
    currency: Currency = Field(default=Currency.EUR, description="The currency code for the budget (e.g., USD, EUR).")

    transportation: str | None = Field(default= None, description= "The description of the tranportation")
    travel_tips: list[str] | None = Field(default_factory=list, sa_column=Column(ARRAY(String)), description="Extra information for the visitors in the form of tips")

    # Weather summary might be unavailable if the travel date is outside the available forecast range.
    weather_summary: str | None = Field(default=None, description="Weather summary for the period which the visitors will visit the place")

    created_at: datetime | None = Field(
        default_factory= lambda: datetime.now(UTC), 
        sa_type=DateTime(timezone=True),  # type: ignore
    )

    search_session : SearchSession = Field(Relationship(back_populates="packages"), description="The search session in which the current travel package was generated")
    itinerary: list["Itinerary"] = Field(Relationship(back_populates="package"), description="A list of itineraries contained in the current travel package") 
    accomondations: list["Accommodation"] = Field(Relationship(back_populates="package"), description="A list of accommodations contained in the current travel package")  

# Itinerary package entity model
class Itinerary(SQLModel, table=True):
    """
    Database entity for the Itinerary.
    Represents an itinerary (a DAILY plan) which consists of activities.
    One record = One day
    """
    id : uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="The unique identifier for the itinerary.")
    travel_package_id: uuid.UUID = Field(foreign_key="travelpackage.id", ondelete="CASCADE")

    day_number:int = Field(description="The number of the day of the itinerary")
    date: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True))
    )
    description: str = Field(description="The description of the day's itinerary")
    estimated_daily_cost: float | None = Field(default=None)

    package: TravelPackage = Relationship(back_populates="itinerary")
    activities: list["Activity"] = Relationship(back_populates="itinerary") 

# Activity entity model
class Activity(SQLModel, table=True):
    """
    Database entity for the Activity.
    Represents an activity that the visitor can take part in.
    """
    id : uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="The unique identifier for the activity.")
    type: ActivityType = Field(default=ActivityType.SIGHTSEEING, description="The type of the activity (sightseeing, adventure or food)")
    itinerary_id: uuid.UUID = Field(foreign_key="itinerary.id", ondelete="CASCADE")
    title: str = Field(max_length=200)
    estimated_cost: float | None = Field(default=None, description="The estimated cost of the activity")
    average_duration_hours: int | None = Field(default=None, description="The average duration of the activity in hours")
    part_of_day: PartOfDay = Field(default=PartOfDay.MORNING, description="The part of the day the activity (morning, afternoon, evening)")

    itinerary: Itinerary = Relationship(back_populates="activities")

# Accommodation entity model
class Accommodation(SQLModel, table = True):
    """
    Database entity for the Accommodation.
    Represents an accommodation a visitor can stay. 
    """
    id : uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="The unique identifier for the accommodation.")
    package_id: uuid.UUID = Field(foreign_key="travelpackage.id", ondelete="CASCADE")
    name:str = Field(max_length=200, description="The name of the accommodation")
    type: AccommodationType = Field(default=AccommodationType.HOTEL, description="The type of the accommodation (hotel or hostel or airbnb).")
    area: str | None = Field(default=None, max_length=100, description="The area in which the accommodation is located at.")
    cost_per_night: float | None = Field(default=None)
    rating: float | None = Field(default=None, description="The rating of the accommodation. Rated from 1.0 to 5.0")
    extra_info: str | None = Field(default=None, description="Any extra information regarding the accommodation")

    package: TravelPackage = Relationship(back_populates="accommodations")















#TODO:Add Accommodation entity model
    


    






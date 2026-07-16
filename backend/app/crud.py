import uuid

from app.enums import SearchSessionStatus
from app.models import SearchSession, SearchSessionCreateDTO, User, UserCreateDTO, UserUpdateDTO, UserUpdateSelfDTO
from sqlmodel import Session, select

# Dummy hash to use for timing attack prevention when user is not found
DUMMY_HASH = "$argon2id$v=19$m=65536,t=3,p=4$MjQyZWE1MzBjYjJlZTI0Yw$YTU4NGM5ZTZmYjE2NzZlZjY0ZWY3ZGRkY2U2OWFjNjk"

#=======================================================================================================
# USER METHODS
#=======================================================================================================

def create_user(*, session:Session, user_creation_data:UserCreateDTO) -> User:
    """
    CRUD method for user creation.
    """
    db_obj = User.model_validate(
        user_creation_data, update = {"hashed_password": get_password_hash(user_creation_data.password)}
    )

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)

    return db_obj

def update_user(*, session:Session, user_update_data:UserUpdateDTO | UserUpdateSelfDTO, user:User) -> User:
    """
    CRUD method for user update.
    Called by superusers using UserUpdateDTO as a parameter.
    Called by regular users using UserUpdateSelfDTO as a parameter. 
    """
    user_data = user_update_data.model_dump(exclude_unset=True)
    extra_data = {}

    if "password" in user_data:
        extra_data["hashed_password"] = get_password_hash(user_data.pop("password"))
    
    user.sqlmodel_update(user_data, update= extra_data)

    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def get_user_by_email(*, session:Session, email:str) -> User | None :
    """
    CRUD method for finding a user by their email.
    """
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()

#=======================================================================================================
# SEARCH SESSION METHODS
#=======================================================================================================

def create_search_session(*, session:Session, owner_id:uuid.UUID, search_session_creation_data: SearchSessionCreateDTO) -> SearchSession:
    """
    CRUD method for search session creation.
    """
    db_obj = User.model_validate(
        search_session_creation_data, update={"owner_id": owner_id}
    )

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)

    return db_obj

def update_search_session_status(*, session:Session, search_session: SearchSession, status: SearchSessionStatus, error_message: str | None) -> SearchSession:
    """
    CRUD method for search session update.
    """
    search_session.status = status
    search_session.error_message = error_message

    session.add(search_session)
    session.commit()
    session.refresh(search_session)

    return search_session

def get_search_session(*, session:Session, search_session_id:uuid.UUID) -> SearchSession :
    """
    CRUD for finding search session using search session id.
    """
    return session.get(SearchSession, search_session_id)



    














def authenticate(*, session: Session, email:str, password:str) -> User | None:
    """
    Method for authenticating the user.
    """
    user = get_user_by_email(session, email)
    if not user:
        # Prevent time attack
        verify_password(password, DUMMY_HASH)
        return None
    
    verified, updated_password_hash = verify_password(password, user.hashed_password)
    if not verified:
        return None
    if updated_password_hash:
        user.hashed_password = updated_password_hash
        session.add(user)
        session.commit()
        session.refresh(user)
    return user


    

    

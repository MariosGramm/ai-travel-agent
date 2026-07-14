from app.models import User, UserCreateDTO, UserUpdateDTO, UserUpdateSelfDTO
from sqlmodel import Session, select

# Dummy hash to use for timing attack prevention when user is not found
DUMMY_HASH = "$argon2id$v=19$m=65536,t=3,p=4$MjQyZWE1MzBjYjJlZTI0Yw$YTU4NGM5ZTZmYjE2NzZlZjY0ZWY3ZGRkY2U2OWFjNjk"

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

def update_user(*, session:Session, user_update_data:UserUpdateDTO | UserUpdateSelfDTO, user:User):
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


    

    

from app.models import User, UserCreateDTO, UserUpdateDTO, UserUpdateSelfDTO
from sqlmodel import Session, select


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




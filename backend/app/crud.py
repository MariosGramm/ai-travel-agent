from app.models import User, UserCreateDTO
from sqlmodel import Session


def create_user(*, session: Session, userCreateDTO: UserCreateDTO ):
    db_obj = User.model_validate(
        userCreateDTO, update = {"hashed_password": get_password_hash(userCreateDTO.password)}
    )

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj
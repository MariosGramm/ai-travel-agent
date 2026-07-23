from datetime import timedelta
from typing import Annotated
from app import crud
from app.models import Token
from app.api.deps import SessionDep
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.core.config import settings

router = APIRouter(tags=["login"])

@router.post("/login/access-token")
def login_access_token(session:SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user=crud.authenticate(session=session, email=form_data.username, password=form_data.password)

    if not user:
        raise HTTPException(status_code=400, detail="Username or password not found")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="User is not active")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    return Token(user.id, expires_delta = access_token_expires)
    




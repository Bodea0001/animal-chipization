from typing import Literal
from sqlalchemy.orm import Session
from fastapi.security import HTTPBasicCredentials
from fastapi import Depends, HTTPException, status

from db import models
from models import schemas
from db.crud import get_user
from controllers.db import get_db
from controllers.auth import security
from controllers.password import verify_password
from controllers.validation import validate_account


def check_role(user: schemas.Account, allowed_roles: list[schemas.Role]):
    if user.role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    

async def get_current_account(
    db: Session = Depends(get_db),
    credentials: HTTPBasicCredentials = Depends(security),
) -> schemas.Account :
    user = get_user(db, credentials.username)
    if not user or not verify_password(credentials.password, user.password):  # type: ignore
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return validate_account(user)

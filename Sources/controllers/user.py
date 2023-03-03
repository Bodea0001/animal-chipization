from sqlalchemy.orm import Session
from fastapi.security import HTTPBasicCredentials
from fastapi import Depends, HTTPException, status

from models import schemas
from db.crud import get_user
from controllers.db import get_db
from controllers.auth import security
from controllers.password import verify_password
from controllers.validation import validate_account


async def get_current_account(
    db: Session = Depends(get_db),
    credentials: HTTPBasicCredentials | None = Depends(security),
) -> schemas.Account | None:
    if not credentials:
        return None
    user = get_user(db, credentials.username)
    if not user or not verify_password(credentials.password, user.password):  # type: ignore
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return validate_account(user)

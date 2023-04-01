from sqlalchemy.orm import Session
from fastapi.security import HTTPBasicCredentials
from fastapi import APIRouter, status, HTTPException, Depends

from models import schemas
from db.crud import create_account, exists_account_with_email
from controllers.db import get_db
from controllers.password import get_password_hash
from controllers.validation import validate_account
from controllers.auth import security_without_auto_error


router = APIRouter()


@router.post(
    path="/registration",
    tags=["registration"],
    response_model=schemas.AccountOut,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового аккаунта",
)
async def process_registration(
    account: schemas.AccountRegistration,
    db: Session = Depends(get_db),
    credentials: HTTPBasicCredentials | None = Depends(security_without_auto_error),
):
    if credentials:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    if exists_account_with_email(db, account.email):  # type: ignore
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)
    
    account.password = get_password_hash(account.password)
    db_account = create_account(db, account)
    return validate_account(db_account)

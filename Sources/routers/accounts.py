from sqlalchemy.orm import Session
from fastapi import APIRouter, status, HTTPException, Depends, Query, Path

from models import schemas
from db.crud import (
    get_accounts, 
    get_user_by_id, 
    update_account,
    delete_account,
    exists_account_with_id, 
    exists_account_with_email,
    is_account_linked_with_animals,
)
from controllers.db import get_db
from controllers.user import get_current_account
from controllers.password import get_password_hash
from controllers.validation import validate_account


router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get(
    path="/search",
    response_model=list[schemas.AccountOut],
    status_code=status.HTTP_200_OK,
    summary="Поиск аккаунтов пользователей по параметрам"
)
async def search_accounts(
    search_data: schemas.AccountSearch = Depends(),
    skip: int = Query(default=0, alias="from", ge=0),
    size: int = Query(default=10, gt=0),
    db: Session = Depends(get_db),
    _: schemas.Account | None = Depends(get_current_account)
): 
    accounts = get_accounts(db, search_data, skip, size)
    if not accounts:
        return []
    valid_accounts = [validate_account(account) for account in accounts]
    return valid_accounts


@router.get(
    path="/{accountId}",
    response_model=schemas.AccountOut,
    status_code=status.HTTP_200_OK,
    summary="Получение информации об аккаунте пользователя"
)
async def get_account_information(
    accountId: int = Path(gt=0),
    db: Session = Depends(get_db),
    _: schemas.Account | None = Depends(get_current_account)
):
    account = get_user_by_id(db, accountId)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return validate_account(account)


@router.put(
    path="/{accountId}",
    response_model=schemas.AccountOut,
    status_code=status.HTTP_200_OK,
    summary="Обновление данных аккаунта пользователя"
)
async def update_account_information(
    update_data: schemas.AccountUpdate,
    accountId: int = Path(gt=0),
    db: Session = Depends(get_db),
    auth_user: schemas.Account | None = Depends(get_current_account)
):
    if not auth_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    if auth_user.id != accountId or not exists_account_with_id(db, accountId):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    if auth_user.email != update_data.email and exists_account_with_email(db, update_data.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)
    
    update_data.password = get_password_hash(update_data.password)
    update_account(db, auth_user.id, update_data)
    return validate_account(get_user_by_id(db, auth_user.id))


@router.delete(
    path="/{accountId}",
    status_code=status.HTTP_200_OK,
    summary="Удаление аккаунта пользователя"
)
async def delete_account_information(
    accountId: int = Path(gt=0),
    db: Session = Depends(get_db),
    auth_user: schemas.Account | None = Depends(get_current_account)
):
    if is_account_linked_with_animals(db, accountId):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    
    if not auth_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    if auth_user.id != accountId or not exists_account_with_id(db, accountId):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    delete_account(db, auth_user.id)

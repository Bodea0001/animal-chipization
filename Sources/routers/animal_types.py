from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, status, Depends

from models import schemas
from db.crud import (
    get_animal_type,
    create_animal_type,
    update_animal_type,
    delete_animal_type,
    exists_animal_type_with_id,
    exists_animal_type_with_type,
    is_animal_type_linked_with_animals,
)
from controllers.db import get_db
from controllers.user import get_current_account
from controllers.validation import validate_animal_type


router = APIRouter(prefix="/animals/types", tags=["animal type"])


@router.post(
    path="",
    response_model=schemas.AnimalType,
    status_code=status.HTTP_201_CREATED,
    summary="Добавление типа животного"
)
async def add_animal_type(
    animal_type: schemas.AnimalTypeBase,
    db: Session = Depends(get_db),
    auth_user: schemas.Account | None = Depends(get_current_account)
):
    if not auth_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    if exists_animal_type_with_type(db, animal_type):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)
    
    db_animal_type = create_animal_type(db, animal_type)
    return validate_animal_type(db_animal_type)


@router.get(
    path="/{typeId}",
    response_model=schemas.AnimalType,
    status_code=status.HTTP_200_OK,
    summary="Получение информации о типе животного"
)
async def get_type(
    typeId: int | None,
    db: Session = Depends(get_db),
    _: schemas.Account | None = Depends(get_current_account)
):
    if not typeId or typeId <=0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    
    animal_type = get_animal_type(db, typeId)
    if not animal_type:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return validate_animal_type(animal_type)


@router.put(
    path="/{typeId}",
    response_model=schemas.AnimalType,
    status_code=status.HTTP_200_OK,
    summary="Изменение типа животного"
)
async def update_type(
    typeId: int | None,
    animal_type: schemas.AnimalTypeBase,
    db: Session = Depends(get_db),
    auth_user: schemas.Account | None = Depends(get_current_account)
):
    if not typeId or typeId <=0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    
    if not auth_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    if not exists_animal_type_with_id(db, typeId):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    if exists_animal_type_with_type(db, animal_type):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)

    update_animal_type(db, typeId, animal_type)
    return validate_animal_type(get_animal_type(db, typeId))


@router.delete(
    path="/{typeId}",
    status_code=status.HTTP_200_OK,
    summary="Удаление типа животного"
)
async def delete_type(
    typeId: int | None,
    db: Session = Depends(get_db),
    auth_user: schemas.Account | None = Depends(get_current_account)
):
    if not typeId or typeId <=0 or is_animal_type_linked_with_animals(db, typeId):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    
    if not auth_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    if not exists_animal_type_with_id(db, typeId):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    delete_animal_type(db, typeId)

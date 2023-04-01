from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, status, Depends, Query, Path

from models import schemas
from db.crud import (
    get_animal,
    get_animals,
    create_animal,
    update_animal,
    delete_animal,
    has_animal_type,
    exists_animal_with_id,
    exists_account_with_id,
    exists_animal_type_with_id,
    update_animal_type_of_animal,
    delete_animal_type_of_animal,
    get_animal_type_of_animal_len,
    exists_location_point_with_id,
    create_animalType_animal_connection,
)
from controllers.db import get_db
from controllers.validation import validate_animal
from controllers.user import get_current_account, check_role


router = APIRouter(prefix="/animals", tags=["animal"])


@router.post(
    path="",
    response_model=schemas.Animal,
    status_code=status.HTTP_201_CREATED,
    summary="Добавление нового животного"
)
async def add_animal(
    animal: schemas.AnimalCreation,
    db: Session = Depends(get_db),
    auth_user: schemas.Account = Depends(get_current_account)
):
    check_role(auth_user.role, [schemas.Role.ADMIN, schemas.Role.CHIPPER])

    for type_id in animal.animalTypes:
        if not exists_animal_type_with_id(db, type_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    if not exists_account_with_id(db, animal.chipperId):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    if not exists_location_point_with_id(db, animal.chippingLocationId):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return validate_animal(create_animal(db, animal))


@router.get(
    path="/search",
    response_model=list[schemas.Animal],
    status_code=status.HTTP_200_OK,
    summary="Поиск животных по параметрам"
)
async def search_animals(
    search_data: schemas.AnimalSearch = Depends(),
    skip: int = Query(default=0, alias="from", ge=0),
    size: int = Query(default=10, gt=0),
    db: Session = Depends(get_db),
    _: schemas.Account = Depends(get_current_account)
):
    animals = get_animals(db, search_data, skip, size)
    return [validate_animal(animal) for animal in animals]


@router.get(
    path="/{animalId}",
    response_model=schemas.Animal,
    status_code=status.HTTP_200_OK,
    summary="Получение информации о животном"
)
async def get_animal_information(
    animalId: int = Path(gt=0),
    db: Session = Depends(get_db),
    _: schemas.Account = Depends(get_current_account)
): 
    animal = get_animal(db, animalId)
    if not animal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return validate_animal(animal)


@router.put(
    path="/{animalId}",
    response_model=schemas.Animal,
    status_code=status.HTTP_200_OK,
    summary="Изменение информации о животном"
)
async def update_animal_information(
    update_data: schemas.AnimalUpdate,
    animalId: int = Path(gt=0),
    db: Session = Depends(get_db),
    auth_user: schemas.Account = Depends(get_current_account)
): 
    check_role(auth_user.role, [schemas.Role.ADMIN, schemas.Role.CHIPPER])

    animal = get_animal(db, animalId)
    if not animal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    if (update_data.lifeStatus == schemas.LifeStatus.ALIVE and
        animal.lifeStatus == schemas.LifeStatus.DEAD):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    
    if (animal.visitedLocations and 
        update_data.chippingLocationId == animal.visitedLocations[0].locationPointId):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    if not exists_account_with_id(db, update_data.chipperId):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    if not exists_location_point_with_id(db, update_data.chippingLocationId):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    update_animal(db, animalId, update_data)
    return validate_animal(get_animal(db, animalId))


@router.delete(
    path="/{animalId}",
    status_code=status.HTTP_200_OK,
    summary="Удаление животного"
)
async def delete_animal_information(
    animalId: int = Path(gt=0),
    db: Session = Depends(get_db),
    auth_user: schemas.Account = Depends(get_current_account)
):
    check_role(auth_user.role, [schemas.Role.ADMIN])

    animal = get_animal(db, animalId)
    if not animal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    if (animal.visitedLocations and
        animal.chippingLocationId != animal.visitedLocations[-1].locationPointId):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    delete_animal(db, animalId)


@router.post(
    path="/{animalId}/types/{typeId}",
    response_model=schemas.Animal,
    status_code=status.HTTP_201_CREATED,
    summary="Добавление типа животного к животному"
)
async def add_animal_type_to_animal(
    animalId: int = Path(gt=0),
    typeId: int = Path(gt=0),
    db: Session = Depends(get_db),
    auth_user: schemas.Account = Depends(get_current_account)
):
    check_role(auth_user.role, [schemas.Role.ADMIN, schemas.Role.CHIPPER])

    if (not exists_animal_with_id(db, animalId) or
        not exists_animal_type_with_id(db, typeId)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    if has_animal_type(db, animalId, typeId):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)
    
    create_animalType_animal_connection(db, animalId, typeId)
    return validate_animal(get_animal(db, animalId))


@router.put(
    path="/{animalId}/types",
    response_model=schemas.Animal,
    status_code=status.HTTP_200_OK,
    summary="Изменение типа животного у животного"
)
async def update_type_of_animal(
    update_data: schemas.AnimalTypeAnimalUpdate,
    animalId: int = Path(gt=0),
    db: Session = Depends(get_db),
    auth_user: schemas.Account = Depends(get_current_account)
):    
    check_role(auth_user.role, [schemas.Role.ADMIN, schemas.Role.CHIPPER])

    if (not exists_animal_with_id(db, animalId) or
        not exists_animal_type_with_id(db, update_data.oldTypeId) or
        not exists_animal_type_with_id(db, update_data.newTypeId) or
        not has_animal_type(db, animalId, update_data.oldTypeId)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    if has_animal_type(db, animalId, update_data.newTypeId):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)

    update_animal_type_of_animal(db, animalId, update_data)
    return validate_animal(get_animal(db, animalId))


@router.delete(
    path="/{animalId}/types/{typeId}",
    status_code=status.HTTP_200_OK,
    summary="Удаление типа животного"
)
async def delete_type_of_animal(
    animalId: int = Path(gt=0),
    typeId: int = Path(gt=0),
    db: Session = Depends(get_db),
    auth_user: schemas.Account = Depends(get_current_account)
):  
    check_role(auth_user.role, [schemas.Role.ADMIN, schemas.Role.CHIPPER])

    if (not exists_animal_with_id(db, animalId) or
        not exists_animal_type_with_id(db, typeId) or
        not has_animal_type(db, animalId, typeId)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    animal_types_of_animal_len = get_animal_type_of_animal_len(db, animalId)
    if animal_types_of_animal_len == 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    delete_animal_type_of_animal(db, animalId, typeId)
    return validate_animal(get_animal(db, animalId))

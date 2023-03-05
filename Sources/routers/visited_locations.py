from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, status, Depends, Query, Path

from models import schemas
from db.crud import (
    get_animal,
    get_visited_location,
    exists_animal_with_id,
    get_visited_locastions,
    update_visited_location,
    delete_visited_location,
    exists_location_point_with_id,
    create_animal_visited_location,
)
from controllers.db import get_db
from controllers.user import get_current_account
from controllers.check import is_point_as_prev_or_next
from controllers.validation import validate_animal, validate_visited_location


router = APIRouter(
    prefix="/animals/{animalId}/locations",
    tags=["animal's visited locations"]
)


@router.get(
    path="",
    response_model=list[schemas.AnimalVisitedLocationOut],
    status_code=status.HTTP_200_OK,
    summary="Просмотр точек локации, посещенных животным"
)
async def search_visited_locations(
    animalId: int = Path(gt=0),
    search_data: schemas.AnimalVisitedLocationSearch = Depends(),
    skip: int = Query(default=0, ge=0, alias="from"),
    size: int = Query(default=10, gt=0),
    db: Session = Depends(get_db),
    _: schemas.Account = Depends(get_current_account)
):
    if not exists_animal_with_id(db, animalId):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    visited_locations = get_visited_locastions(db, animalId, search_data, skip, size)
    return [validate_visited_location(loc) for loc in visited_locations]


@router.post(
    path="/{pointId}",
    response_model=schemas.AnimalVisitedLocationOut,
    status_code=status.HTTP_201_CREATED,
    summary="Добавление точки локации, посещённой животным"
)
async def add_location_point(
    animalId: int = Path(gt=0),
    pointId: int = Path(gt=0),
    db: Session = Depends(get_db),
    auth_user: schemas.Account = Depends(get_current_account)
):
    if not auth_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    if not exists_location_point_with_id(db, pointId):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    animal = get_animal(db, animalId)
    if not animal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if (animal.lifeStatus == schemas.LifeStatus.DEAD or
        not animal.visitedLocations and pointId == animal.chippingLocationId or
        (animal.visitedLocations and 
        pointId == animal.visitedLocations[-1].locationPointId)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    
    visited_location = create_animal_visited_location(db, animalId, pointId)
    return validate_visited_location(visited_location)


@router.put(
    path="",
    response_model=schemas.AnimalVisitedLocationOut,
    status_code=status.HTTP_200_OK,
    summary="Изменение точки локации, посещенной животным"
)
async def change_visited_location(
    change_data: schemas.AnimalVisitedLocationChange,
    animalId: int = Path(gt=0),
    db: Session = Depends(get_db),
    auth_user: schemas.Account = Depends(get_current_account)
):
    if not auth_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    if not exists_location_point_with_id(db, change_data.locationPointId):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    visited_location = get_visited_location(db, change_data.visitedLocationPointId)
    if not visited_location or visited_location.id_animal != animalId:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    if visited_location.locationPointId == change_data.locationPointId:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    
    animal = get_animal(db, animalId)
    if not animal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if (animal.visitedLocations[0].id == change_data.visitedLocationPointId and
        change_data.locationPointId == animal.chippingLocationId or
        is_point_as_prev_or_next(change_data, animal.visitedLocations)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    update_visited_location(db, change_data)

    updated_visited_location = get_visited_location(
        db, change_data.visitedLocationPointId)
    return validate_visited_location(updated_visited_location)


@router.delete(
    path="/{visitedPointId}",
    status_code=status.HTTP_200_OK,
    summary="Удаление точки локации, посещенной животным"
)
async def delete_animal_visited_location(
    animalId: int = Path(gt=0),
    visitedPointId: int = Path(gt=0),
    db: Session = Depends(get_db),
    auth_user: schemas.Account = Depends(get_current_account)
):
    if not auth_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    visited_location = get_visited_location(db, visitedPointId)
    if not visited_location or visited_location.id_animal != animalId:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    animal = get_animal(db, animalId)
    if not animal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    if (len(animal.visitedLocations) >=2 and
        animal.visitedLocations[0].id == visitedPointId and 
        animal.visitedLocations[1].locationPointId == animal.chippingLocationId):
        delete_visited_location(db, animal.visitedLocations[1].id)
    
    delete_visited_location(db, visitedPointId)
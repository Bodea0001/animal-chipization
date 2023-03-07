from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, status, Depends, Path

from models import schemas
from db.crud import (
    get_location_point,
    create_location_point,
    update_location_point,
    delete_location_point,
    exists_location_point_with_id,
    is_location_point_linked_with_animals,
    exists_location_point_with_latitude_and_longitude,
)
from controllers.db import get_db
from controllers.user import get_current_account
from controllers.validation import validate_location_point


router = APIRouter(prefix="/locations", tags=["locations"])


@router.post(
    path="",
    response_model=schemas.LocationPoint,
    status_code=status.HTTP_201_CREATED,
    summary="Добавление точки локации животных"
)
async def add_location_point(
    location_point: schemas.LocationPointBase,
    db: Session = Depends(get_db),
    auth_user: schemas.Account | None = Depends(get_current_account)
):
    if not auth_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    if exists_location_point_with_latitude_and_longitude(db, location_point):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)
    
    db_location_point = create_location_point(db, location_point)
    return validate_location_point(db_location_point)


@router.get(
    path="/{pointId}",
    response_model=schemas.LocationPoint,
    status_code=status.HTTP_200_OK,
    summary="Получение информации о точке локации животных"
)
async def get_location(
    pointId: int = Path(gt=0),
    db: Session = Depends(get_db),
    _: schemas.Account | None = Depends(get_current_account)
):
    location_point = get_location_point(db, pointId)
    if not location_point:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return validate_location_point(location_point)


@router.put(
    path="/{pointId}",
    response_model=schemas.LocationPoint,
    status_code=status.HTTP_200_OK,
    summary="Изменение точки локации животных"
)
async def update_location(
    location_point: schemas.LocationPointBase,
    pointId: int = Path(gt=0),
    db: Session = Depends(get_db),
    auth_user: schemas.Account | None = Depends(get_current_account)
):
    if not auth_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    if not exists_location_point_with_id(db, pointId):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    if exists_location_point_with_latitude_and_longitude(db, location_point):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)

    update_location_point(db, pointId, location_point)
    return validate_location_point(get_location_point(db, pointId))


@router.delete(
    path="/{pointId}",
    status_code=status.HTTP_200_OK,
    summary="Удаление точки локации животных"
)
async def delete_location(
    pointId: int = Path(gt=0),
    db: Session = Depends(get_db),
    auth_user: schemas.Account | None = Depends(get_current_account)
):
    if is_location_point_linked_with_animals(db, pointId):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    
    if not auth_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    if not exists_location_point_with_id(db, pointId):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    delete_location_point(db, pointId)


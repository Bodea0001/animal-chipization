import base64
import pygeohash as pgh
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, status, Depends, Path
from fastapi.responses import PlainTextResponse

from models import schemas
from db.crud import (
    get_location_point,
    create_location_point,
    update_location_point,
    delete_location_point,
    is_point_used_as_visited,
    is_point_used_as_chipping,
    get_location_point_by_coords,
    exists_location_point_with_id,
    is_location_point_linked_with_animals,
    exists_location_point_with_latitude_and_longitude,
)
from controllers.db import get_db
from controllers.validation import validate_location_point
from controllers.user import get_current_account, check_role


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
    auth_user: schemas.Account = Depends(get_current_account)
):
    check_role(auth_user.role, [schemas.Role.ADMIN, schemas.Role.CHIPPER])

    if exists_location_point_with_latitude_and_longitude(db, location_point):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)
    
    db_location_point = create_location_point(db, location_point)
    return validate_location_point(db_location_point)


@router.get(path="", status_code=status.HTTP_200_OK)
async def get_location_by_coords(
    coords: schemas.LocationPointBase = Depends(),
    db: Session = Depends(get_db),
    _: schemas.Account = Depends(get_current_account)
):
    location_point = get_location_point_by_coords(db, coords)
    if not location_point:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return location_point.id


@router.get(
    path="/geohash",
    status_code=status.HTTP_200_OK,
    response_class=PlainTextResponse
)
async def get_location_hash(
    coords: schemas.LocationPointBase = Depends(),
    db: Session = Depends(get_db),
    _: schemas.Account = Depends(get_current_account)
):
    location_point = get_location_point_by_coords(db, coords)
    if not location_point:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return pgh.encode(coords.latitude, coords.longitude)


@router.get(
    path="/geohashv2",
    status_code=status.HTTP_200_OK,
    response_class=PlainTextResponse
)
async def get_location_hash_v2(
    coords: schemas.LocationPointBase = Depends(),
    db: Session = Depends(get_db),
    _: schemas.Account = Depends(get_current_account)
):
    location_point = get_location_point_by_coords(db, coords)
    if not location_point:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    geohash = pgh.encode(coords.latitude, coords.longitude)
    return base64.b64encode(geohash.encode()).decode()


@router.get(
    path="/geohashv3",
    status_code=status.HTTP_200_OK,
    response_class=PlainTextResponse
)
async def get_location_hash_v3(
    coords: schemas.LocationPointBase = Depends(),
    db: Session = Depends(get_db),
    _: schemas.Account = Depends(get_current_account)
):
    location_point = get_location_point_by_coords(db, coords)
    if not location_point:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return pgh.encode(coords.latitude, coords.longitude)


@router.get(
    path="/{pointId}",
    response_model=schemas.LocationPoint,
    status_code=status.HTTP_200_OK,
    summary="Получение информации о точке локации животных"
)
async def get_location(
    pointId: int = Path(gt=0),
    db: Session = Depends(get_db),
    _: schemas.Account = Depends(get_current_account)
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
    auth_user: schemas.Account = Depends(get_current_account)
):
    check_role(auth_user.role, [schemas.Role.ADMIN, schemas.Role.CHIPPER])

    if not exists_location_point_with_id(db, pointId):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    if is_point_used_as_chipping(db, pointId) or is_point_used_as_visited(db, pointId):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    
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
    auth_user: schemas.Account = Depends(get_current_account)
):
    check_role(auth_user.role, [schemas.Role.ADMIN])

    if is_location_point_linked_with_animals(db, pointId):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    
    if not auth_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    if not exists_location_point_with_id(db, pointId):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    delete_location_point(db, pointId)


from shapely import Polygon
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, status, Depends, Path

from models import schemas
from db.crud import (
    get_area,
    create_area,
    update_area,
    delete_area,
    get_all_areas,
    get_area_by_name,
    exists_area_with_id,
    exists_area_with_name
)
from controllers.db import get_db
from controllers.validation import validate_area_out
from controllers.user import get_current_account, check_role
from controllers.check import check_border_intersect_in_polygon
from controllers.area import get_polygon


router = APIRouter(prefix="/areas", tags=["areas"])


@router.get(
    path="/{areaId}",
    response_model=schemas.AreaOut,
    status_code=status.HTTP_200_OK,
    summary="Получение информации о зоне"
)
async def get_current_area(
    areaId: int = Path(gt=0),
    db: Session = Depends(get_db),
    _: schemas.Account = Depends(get_current_account)
):
    area = get_area(db, areaId)
    if not area:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    return validate_area_out(area)


@router.post(
    path="",
    response_model=schemas.AreaOut,
    status_code=status.HTTP_201_CREATED,
    summary="Добавление зоны"
)
async def add_area(
    new_area: schemas.AreaCreate,
    db: Session = Depends(get_db),
    auth_user: schemas.Account = Depends(get_current_account)
):
    check_role(auth_user.role, [schemas.Role.ADMIN])

    if exists_area_with_name(db, new_area.name):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)

    new_polygon = get_polygon(new_area.areaPoints)

    if new_polygon.area == 0:
        print("polygon area")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    
    check_border_intersect_in_polygon(new_polygon)

    areas = get_all_areas(db)
    for area in areas:  # type: ignore
        area_polygon = Polygon([(point.latitude, point.longitude) 
                                for point in area.areaPoints]) 
        
        if new_polygon.equals(area_polygon):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT)
        if (not new_polygon.touches(area_polygon) and 
            new_polygon.intersects(area_polygon) or
            new_polygon.contains(area_polygon) or
            area_polygon.contains(new_polygon)):
            print("new polygon:", new_polygon, "old polygon:", area_polygon)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    
    db_area = create_area(db, new_area)
    return validate_area_out(db_area)


@router.put(
    path="/{areaId}",
    response_model=schemas.AreaOut,
    status_code=status.HTTP_200_OK,
    summary="Обновление зоны"
)
async def update_current_area(
    upd_area: schemas.AreaUpdate,
    areaId: int = Path(gt=0),
    db: Session = Depends(get_db),
    auth_user: schemas.Account = Depends(get_current_account)
):
    check_role(auth_user.role, [schemas.Role.ADMIN])

    if not exists_area_with_id(db, areaId):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    named_area = get_area_by_name(db, upd_area.name)
    if named_area and named_area.id != areaId:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)

    upd_polygon = get_polygon(upd_area.areaPoints)

    if upd_polygon == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    
    check_border_intersect_in_polygon(upd_polygon)

    areas = get_all_areas(db)
    for area in areas:  # type: ignore
        if areaId == area.id:
            continue

        area_polygon = Polygon([(point.latitude, point.longitude) 
                                for point in area.areaPoints])
        
        if upd_polygon.equals(area_polygon):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT)
        if (upd_polygon.intersects(area_polygon) or
            upd_polygon.contains(area_polygon) or
            area_polygon.contains(upd_polygon)):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    
    update_area(db, areaId, upd_area)
    return validate_area_out(get_area(db, areaId))


@router.delete(
    path="/{areaId}",
    status_code=status.HTTP_200_OK,
    summary="Удаление зоны"
)
async def delete_current_area(
    areaId: int = Path(gt=0),
    db: Session = Depends(get_db),
    auth_user: schemas.Account = Depends(get_current_account)
):
    check_role(auth_user.role, [schemas.Role.ADMIN])

    if not exists_area_with_id(db, areaId):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    delete_area(db, areaId)


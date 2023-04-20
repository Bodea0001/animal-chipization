from shapely import Polygon, Point
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, status, Depends, Path

from models import schemas
from controllers.db import get_db
from controllers.area import get_polygon
from controllers.analytics import (
    create_types_analytics,
    save_animals_with_vis_loc_in_area,
    save_animals_with_chip_loc_in_area,
    save_and_sort_animals_with_vis_locs_in_area,
)
from controllers.validation import validate_area_out
from controllers.user import get_current_account, check_role
from db.crud import (
    get_area,
    create_area,
    update_area,
    delete_area,
    get_all_areas,
    get_area_by_name,
    exists_area_with_id,
    exists_area_with_name,
    get_last_visited_locations,
    get_visited_locations_per_interval,
    get_animals_with_chip_loc_per_interval,
    get_animals_without_vis_locs_and_with_chip_loc_before_date
)
from controllers.check import check_border_intersect_in_polygon


router = APIRouter(prefix="/areas", tags=["areas"])


@router.get(
    path="/{areaId}",
    response_model=schemas.AreaOut,
    status_code=status.HTTP_200_OK,
    summary="Получение информации о зоне",
)
async def get_current_area(
    areaId: int = Path(gt=0),
    db: Session = Depends(get_db),
    _: schemas.Account = Depends(get_current_account),
):
    area = get_area(db, areaId)
    if not area:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return validate_area_out(area)


@router.post(
    path="",
    response_model=schemas.AreaOut,
    status_code=status.HTTP_201_CREATED,
    summary="Добавление зоны",
)
async def add_area(
    new_area: schemas.AreaCreate,
    db: Session = Depends(get_db),
    auth_user: schemas.Account = Depends(get_current_account),
):
    check_role(auth_user.role, [schemas.Role.ADMIN])

    if exists_area_with_name(db, new_area.name):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)

    new_polygon = get_polygon(new_area.areaPoints)

    if new_polygon.area == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    check_border_intersect_in_polygon(new_polygon)

    areas = get_all_areas(db)
    for area in areas:  # type: ignore
        area_polygon = Polygon(
            [(point.latitude, point.longitude) for point in area.areaPoints]
        )

        if new_polygon.equals(area_polygon):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT)
        if (
            not new_polygon.touches(area_polygon)
            and new_polygon.intersects(area_polygon)
            or new_polygon.contains(area_polygon)
            or area_polygon.contains(new_polygon)
        ):
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
        if (
            upd_polygon.intersects(area_polygon)
            or upd_polygon.contains(area_polygon)
            or area_polygon.contains(upd_polygon)
        ):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    
    update_area(db, areaId, upd_area)
    return validate_area_out(get_area(db, areaId))


@router.delete(
    path="/{areaId}", status_code=status.HTTP_200_OK, summary="Удаление зоны"
)
async def delete_current_area(
    areaId: int = Path(gt=0),
    db: Session = Depends(get_db),
    auth_user: schemas.Account = Depends(get_current_account),
):
    check_role(auth_user.role, [schemas.Role.ADMIN])

    if not exists_area_with_id(db, areaId):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    delete_area(db, areaId)


@router.get(
    path="/{areaId}/analytics",
    tags=["analytics"],
    response_model=schemas.AreaAnalytics,
    status_code=status.HTTP_200_OK,
    summary="Просмотр информации о перемещениях животных в зоне",
)
async def get_area_analytics(
    interval: schemas.AreaAnalyticsInterval = Depends(),
    areaId: int = Path(gt=0),
    db: Session = Depends(get_db),
    _: schemas.Account = Depends(get_current_account),
):
    area = get_area(db, areaId)
    if not area:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    polygon = get_polygon(area.areaPoints)

    quantity_animal_ids =  set()
    arrived_animal_ids = set()
    gone_animal_ids = set()

    # Берем последние посещенные локации, которые животные посетили до начала
    # интервала и сохраняем тех животных, чьи последние посещенные локации
    # находятся в зоне, по которой идет аналитика
    last_vis_locs_bef_start_date = get_last_visited_locations(db, interval.startDate)
    save_animals_with_vis_loc_in_area(
        quantity_animal_ids, polygon, last_vis_locs_bef_start_date)

    # Берем животных, у которых чипирование было до начала интервала и нет
    # посещенных локаций и животных, чье чипирование было во время интервала.
    # Сохраняем тех животных, чье чипирование было в зоне аналитики
    animals_1 = get_animals_without_vis_locs_and_with_chip_loc_before_date(
            db, interval.startDate)
    animals_2 = get_animals_with_chip_loc_per_interval(
            db, interval.startDate, interval.endDate)
    animals = animals_1 + animals_2
    save_animals_with_chip_loc_in_area(db, quantity_animal_ids, polygon, animals)  # type: ignore

    # Берем посещенные локации, которые животные посетили в период интервала.
    # Сохраняем животных, чьи посещенные локации находятся в зоне и сортируем
    # животных по находившимся в зоне, посетившим зону и вышедшим из зоны.
    vis_locs_per_interval = get_visited_locations_per_interval(
        db, interval.startDate, interval.endDate)
    save_and_sort_animals_with_vis_locs_in_area(
        quantity_animal_ids,
        arrived_animal_ids,
        gone_animal_ids,
        polygon,
        vis_locs_per_interval
    )

    # Создаем аналитику для каждого типа животного
    types_analytics = create_types_analytics(
        db, quantity_animal_ids, arrived_animal_ids, gone_animal_ids)

    return schemas.AreaAnalytics(
        totalQuantityAnimals=len(quantity_animal_ids),
        totalAnimalsArrived=len(arrived_animal_ids),
        totalAnimalsGone=len(gone_animal_ids),
        animalsAnalytics=types_analytics
    )

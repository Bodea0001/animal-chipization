from pydantic import EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, exists, and_, or_, not_, cast, Date, func
from datetime import date

from db import models
from models import schemas


# Account ---------------------------------------------------------------------
def create_account(
    db: Session, 
    account: schemas.AccountRegistration
) -> models.Account:
    db_account = models.Account(
        firstName = account.firstName,
        lastName = account.lastName,
        email=account.email,
        password=account.password
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


def create_account_with_role(
    db: Session, 
    account: schemas.AccountAdding
) -> models.Account:
    db_account = models.Account(
        firstName = account.firstName,
        lastName = account.lastName,
        email=account.email,
        password=account.password,
        role=account.role
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


def exists_account_with_email(db: Session, email: str | EmailStr) -> bool:
    return db.query(exists().where(models.Account.email==email)).scalar()


def exists_account_with_id(db: Session, id: int | Column[Integer]) -> bool:
    return db.query(exists().where(models.Account.id==id)).scalar()    


def get_user(db: Session, email: str) -> models.Account | None:
    return db.query(models.Account).filter(models.Account.email==email).first()


def get_user_by_id(db: Session, id: int | Column[Integer]) -> models.Account | None:
    return db.query(models.Account).filter(models.Account.id == id).first()


def get_accounts(
    db: Session,
    data: schemas.AccountSearch,
    skip: int,
    size: int
) -> list[models.Account] | list[None]:
    dct = {
        0: models.Account.firstName,
        1: models.Account.lastName,
        2: models.Account.email,
    }
    args = (data.firstName, data.lastName, data.email)
    lst = [dct[i].ilike(f"%{arg}%") for i, arg in enumerate(args) if arg]
    return db.query(models.Account).filter(and_(*lst)).order_by(
        models.Account.id).offset(skip).limit(size).all()


def update_account(
    db: Session, 
    account_id: int | Column[Integer], 
    user_data: schemas.AccountUpdate
):
    db.query(models.Account).filter(models.Account.id == account_id).update(
        {
            models.Account.firstName: user_data.firstName,
            models.Account.lastName: user_data.lastName,
            models.Account.email: user_data.email,
            models.Account.password: user_data.password,
            models.Account.role: user_data.role
        },
        synchronize_session=False
    )
    db.commit()


def delete_account(
    db: Session,
    account_id: int | Column[Integer]
):
    db.query(models.Account).filter(models.Account.id==account_id).delete()
    db.commit()


def is_account_linked_with_animals(
    db: Session,
    account_id: int | Column[Integer]
) -> bool:
    return db.query(exists().where(models.Animal.chipperId==account_id)).scalar()    


# LocationPoint ---------------------------------------------------------------
def get_location_point(
    db: Session,
    point_id: int | Column[Integer]
) -> models.LocationPoint | None:
    return db.query(models.LocationPoint).filter(
        models.LocationPoint.id==point_id
    ).first()


def get_location_point_by_coords(
    db: Session,
    coords: schemas.LocationPointBase
) -> models.LocationPoint | None:
    return db.query(models.LocationPoint).filter(
        models.LocationPoint.latitude == coords.latitude,
        models.LocationPoint.longitude == coords.longitude
    ).first()


def exists_location_point_with_latitude_and_longitude(
    db: Session, 
    location_point: schemas.LocationPointBase
) -> bool:
    return db.query(exists().where(
        models.LocationPoint.latitude == location_point.latitude,
        models.LocationPoint.longitude == location_point.longitude
    )).scalar()    


def exists_location_point_with_id(db: Session, point_id: int) -> bool:
    return db.query(exists().where(models.LocationPoint.id == point_id)).scalar()


def is_point_used_as_chipping(db: Session, point_id: int) -> bool:
    return db.query(
        exists().where(models.Animal.chippingLocationId == point_id)).scalar()


def is_point_used_as_visited(db: Session, point_id: int) -> bool:
    return db.query(
        exists().where(models.AnimalVisitedLocation.locationPointId == point_id)
    ).scalar()


def create_location_point(
    db: Session,
    location_point: schemas.LocationPointBase
) -> models.LocationPoint:
    db_location_point = models.LocationPoint(
        latitude = location_point.latitude,
        longitude = location_point.longitude
    )
    db.add(db_location_point)
    db.commit()
    db.refresh(db_location_point)
    return db_location_point


def update_location_point(
    db: Session,
    point_id: int | Column[Integer],
    location_point: schemas.LocationPointBase
):
    db.query(models.LocationPoint).filter(
        models.LocationPoint.id == point_id
    ).update(
        {
            models.LocationPoint.latitude: location_point.latitude,
            models.LocationPoint.longitude: location_point.longitude
        },
        synchronize_session=False
    )
    db.commit()


def is_location_point_linked_with_animals(
    db: Session,
    point_id: int | Column[Integer]
) -> bool:
    animals_link = db.query(exists().where(
        models.Animal.chippingLocationId == point_id
    )).scalar()

    animals_visited_locations_link = db.query(exists().where(
        models.AnimalVisitedLocation.locationPointId == point_id
    )).scalar()

    return any((animals_link, animals_visited_locations_link))


def delete_location_point(db: Session, point_id: int | Column[Integer]):
    db.query(models.LocationPoint).filter(
        models.LocationPoint.id == point_id
    ).delete()
    db.commit()


# AnimalTypes -----------------------------------------------------------------
def get_animal_type(
    db: Session,
    type_id: int | Column[Integer]
) -> models.AnimalType | None:
    return db.query(models.AnimalType).filter(
        models.AnimalType.id == type_id
    ).first()


def exists_animal_type_with_type(
    db: Session, 
    animal_type: schemas.AnimalTypeBase
) -> bool:
    return db.query(exists().where(
        models.AnimalType.type == animal_type.type,
    )).scalar()    


def exists_animal_type_with_id(db: Session, type_id: int) -> bool:
    return db.query(exists().where(models.AnimalType.id == type_id)).scalar()


def create_animal_type(
    db: Session,
    animal_type: schemas.AnimalTypeBase
) -> models.AnimalType:
    db_animal_type = models.AnimalType(type=animal_type.type)
    db.add(db_animal_type)
    db.commit()
    db.refresh(db_animal_type)
    return db_animal_type


def update_animal_type(
    db: Session,
    type_id: int | Column[Integer],
    animal_type: schemas.AnimalTypeBase
):
    db.query(models.AnimalType).filter(models.AnimalType.id==type_id).update(
        {
            models.AnimalType.type: animal_type.type
        },
        synchronize_session=False
    )
    db.commit()


def is_animal_type_linked_with_animals(db: Session, type_id: int) -> bool:
    return db.query(exists().where(
        models.AnimalTypeAnimal.id_animal_type == type_id
    )).scalar()


def delete_animal_type(db: Session, type_id: int | Column[Integer]):
    db.query(models.AnimalType).filter(models.AnimalType.id == type_id).delete()
    db.commit()


# Animal ----------------------------------------------------------------------
def get_animal(db: Session, animal_id: int | Column[Integer]) -> models.Animal | None:
    return db.query(models.Animal).filter(models.Animal.id==animal_id).first()


def get_animals(
    db: Session,
    data: schemas.AnimalSearch,
    skip: int,
    size: int
) -> list[models.Animal] | list[None]:
    datetime_comprasion = []
    if data.startDateTime:
        datetime_comprasion.append(
            models.Animal.chippingDateTime >= data.startDateTime
        )
    if data.endDateTime:
        datetime_comprasion.append(
            models.Animal.chippingDateTime <= data.endDateTime
        )
    dct = {
        0: models.Animal.chipperId,
        1: models.Animal.chippingLocationId,
        2: models.Animal.lifeStatus,
        3: models.Animal.gender,
    }
    args = (data.chipperId,data.chippingLocationId,data.lifeStatus,data.gender)
    args_equality = [dct[i] == value for i, value in enumerate(args) if value]
    return db.query(models.Animal).filter(
        and_(*datetime_comprasion),  # type: ignore
        and_(*args_equality)
    ).order_by(models.Animal.id).offset(skip).limit(size).all()


def create_animal(db: Session, animal: schemas.AnimalCreation) -> models.Animal:
    db_animal = models.Animal(
        weight = animal.weight,
        length = animal.length,
        height = animal.height,
        gender = animal.gender,
        chipperId = animal.chipperId,
        chippingLocationId = animal.chippingLocationId
    )
    db.add(db_animal)
    db.commit()
    db.refresh(db_animal)
    for type_id in animal.animalTypes:
        create_animalType_animal_connection(db, db_animal.id, type_id)
    return db_animal


def create_animalType_animal_connection(
    db: Session,
    animal_id: int | Column[int],
    type_id: int | Column[int]
):
    connection = models.AnimalTypeAnimal(
        id_animal = animal_id,
        id_animal_type = type_id
    )
    db.add(connection)
    db.commit()


def update_animal(db: Session, animal_id: int, data: schemas.AnimalUpdate):
    db.query(models.Animal).filter(models.Animal.id == animal_id).update(
        {
            models.Animal.weight: data.weight,
            models.Animal.length: data.length,
            models.Animal.height: data.height,
            models.Animal.gender: data.gender,
            models.Animal.lifeStatus: data.lifeStatus,
            models.Animal.deathDateTime: data.deathDateTime,
            models.Animal.chipperId: data.chipperId,
            models.Animal.chippingLocationId: data.chippingLocationId,
        },
        synchronize_session=False
    )
    db.commit()


def delete_animal(db: Session, animal_id: int | Column[int]):
    db.query(models.Animal).filter(models.Animal.id==animal_id).delete()
    db.commit()


def exists_animal_with_id(db: Session, animal_id: int) -> bool:
    return db.query(exists().where(models.Animal.id==animal_id)).scalar()


def has_animal_type(
    db: Session,
    animal_id: int | Column[int],
    type_id: int | Column[int]
) -> bool:
    return db.query(exists().where(
        models.AnimalTypeAnimal.id_animal == animal_id,
        models.AnimalTypeAnimal.id_animal_type == type_id
    )).scalar()


def update_animal_type_of_animal(
    db: Session,
    animal_id: int | Column[int],
    data: schemas.AnimalTypeAnimalUpdate
):
    db.query(models.AnimalTypeAnimal).filter(
        models.AnimalTypeAnimal.id_animal == animal_id,
        models.AnimalTypeAnimal.id_animal_type == data.oldTypeId
    ).update(
        {
            models.AnimalTypeAnimal.id_animal_type: data.newTypeId
        },
        synchronize_session=False
    )
    db.commit()


def get_animal_type_of_animal_len(db: Session, animal_id: int | Column[int]) -> int:
    return db.query(models.AnimalTypeAnimal).filter(
        models.AnimalTypeAnimal.id_animal == animal_id
    ).count()


def delete_animal_type_of_animal(
    db: Session, 
    animal_id: int | Column[int],
    type_id: int | Column[int]
):
    db.query(models.AnimalTypeAnimal).filter(
        models.AnimalTypeAnimal.id_animal == animal_id,
        models.AnimalTypeAnimal.id_animal_type == type_id,
    ).delete()
    db.commit()


def get_visited_locastions(
    db: Session,
    animal_id: int,
    data: schemas.AnimalVisitedLocationSearch,
    skip: int,
    size: int
) -> list[models.AnimalVisitedLocation] | list[None]:
    datetime_comprasion = []
    if data.startDateTime:
        datetime_comprasion.append(
            models.AnimalVisitedLocation.dateTimeOfVisitLocationPoint >= data.startDateTime
        )
    if data.endDateTime:
        datetime_comprasion.append(
            models.AnimalVisitedLocation.dateTimeOfVisitLocationPoint <= data.endDateTime
        )
    return db.query(models.AnimalVisitedLocation).filter(
        models.AnimalVisitedLocation.id_animal == animal_id,
        and_(*datetime_comprasion),
    ).order_by(
        models.AnimalVisitedLocation.dateTimeOfVisitLocationPoint
    ).offset(skip).limit(size).all()


def create_animal_visited_location(
    db: Session,
    animal_id: int | Column[int],
    point_id: int | Column[int]
) -> models.AnimalVisitedLocation:
    db_visited_location = models.AnimalVisitedLocation(
        id_animal = animal_id,
        locationPointId = point_id,
    )
    db.add(db_visited_location)
    db.commit()
    db.refresh(db_visited_location)
    return db_visited_location


def get_visited_location(
    db: Session, 
    loc_id: int | Column[int],
) -> models.AnimalVisitedLocation | None:
    return db.query(models.AnimalVisitedLocation).filter(
        models.AnimalVisitedLocation.id == loc_id,
    ).first()


def update_visited_location(db: Session, data: schemas.AnimalVisitedLocationChange):
    db.query(models.AnimalVisitedLocation).filter(
        models.AnimalVisitedLocation.id == data.visitedLocationPointId
    ).update(
        {
            models.AnimalVisitedLocation.locationPointId: data.locationPointId,
        },
        synchronize_session=False
    )
    db.commit()


def delete_visited_location(db: Session, loc_id: int | Column[int]):
    db.query(models.AnimalVisitedLocation).filter(
        models.AnimalVisitedLocation.id == loc_id
    ).delete()
    db.commit()


# Area ------------------------------------------------------------------------
def get_area(db: Session, id: int | Column[int]) -> models.Area | None:
    return db.query(models.Area).filter(models.Area.id == id).first()


def get_all_areas(db: Session) -> list[models.Area] | None:
    return db.query(models.Area).all()


def get_area_by_name(db: Session, name: str) -> models.Area | None:
    return db.query(models.Area).filter(models.Area.name == name).first()


def exists_area_with_name(db: Session, name: str) -> bool:
    return db.query(exists().where(models.Area.name == name)).scalar()


def exists_area_with_id(db: Session, id: int) -> bool:
    return db.query(exists().where(models.Area.id == id)).scalar()


def create_area(db: Session, data: schemas.AreaCreate) -> models.Area:
    area = models.Area(name = data.name)
    db.add(area)
    db.commit()
    db.refresh(area)
    for point in data.areaPoints:
        _create_area_point(db, area.id, point)
    return area


def _create_area_point(db: Session, area_id: int | Column[int], point: schemas.Point):
    area_point = models.AreaPoints(
        id_area = area_id,
        latitude = point.latitude,
        longitude = point.longitude
    )
    db.add(area_point)
    db.commit()


def update_area(db: Session, id: int | Column[int], data: schemas.AreaUpdate):
    db.query(models.Area).filter(models.Area.id == id).update(
        {models.Area.name: data.name,},
        synchronize_session=False
    )
    db.commit()

    _delete_area_points(db, id)
    for point in data.areaPoints:
        _create_area_point(db, id, point)


def _delete_area_points(db: Session, area_id: int | Column[int]):
    db.query(models.AreaPoints).filter(models.AreaPoints.id_area == area_id).delete()
    db.commit()


def delete_area(db: Session, id: int | Column[int]):
    db.query(models.Area).filter(models.Area.id == id).delete()
    db.commit()


# Area's analytics ------------------------------------------------------------
def get_last_visited_locations(
    db: Session, date: date) -> list[models.AnimalVisitedLocation] | None:
    subq = db.query(
        models.AnimalVisitedLocation.id_animal.label("id_animal"), 
        func.max(models.AnimalVisitedLocation.dateTimeOfVisitLocationPoint).label("max_date")
    ).filter(
        cast(models.AnimalVisitedLocation.dateTimeOfVisitLocationPoint, Date) < date
    ).group_by(models.AnimalVisitedLocation.id_animal).subquery()

    return db.query(models.AnimalVisitedLocation).join(
        subq, 
        and_(models.AnimalVisitedLocation.id_animal == subq.c.id_animal, 
        models.AnimalVisitedLocation.dateTimeOfVisitLocationPoint == subq.c.max_date)
    ).all()


def get_visited_locations_per_interval(
    db: Session, 
    start_date: date,
    end_date: date
) -> list[models.AnimalVisitedLocation] | None:
    return db.query(models.AnimalVisitedLocation).filter(
        and_(
            cast(models.AnimalVisitedLocation.dateTimeOfVisitLocationPoint, Date) >= start_date,
            cast(models.AnimalVisitedLocation.dateTimeOfVisitLocationPoint, Date) <= end_date,
            )
    ).order_by(models.AnimalVisitedLocation.dateTimeOfVisitLocationPoint).all()


def get_animals_without_vis_locs_and_with_chip_loc_before_date(
    db: Session,
    date: date,
) -> list[models.Animal] | list[None]:
    subq = db.query(models.AnimalVisitedLocation).filter(
        cast(models.AnimalVisitedLocation.dateTimeOfVisitLocationPoint, Date) < date
    ).subquery()

    return db.query(models.Animal).outerjoin(subq).filter(
        models.AnimalVisitedLocation.id_animal == None,
        cast(models.Animal.chippingDateTime, Date) < date 
    ).all()


def get_animals_with_chip_loc_per_interval(
    db: Session,
    start_date: date,
    end_date: date,
) -> list[models.Animal] | list[None]:
    return db.query(models.Animal).filter(
        cast(models.Animal.chippingDateTime, Date) >= start_date, 
        cast(models.Animal.chippingDateTime, Date) <= end_date 
    ).all()


def get_animal_types(db: Session, animal_id: int | Column[int]) -> list[models.AnimalType]:
    subq = db.query(models.AnimalTypeAnimal).filter(
        models.AnimalTypeAnimal.id_animal == animal_id
    ).subquery()

    return db.query(models.AnimalType).join(subq).all()

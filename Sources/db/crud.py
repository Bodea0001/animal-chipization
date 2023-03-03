from pydantic import EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, exists, and_

from db import models
from models import schemas


# Account
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
            models.Account.password: user_data.password
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


# LocationPoint
def get_location_point(
    db: Session,
    point_id: int | Column[Integer]
) -> models.LocationPoint | None:
    return db.query(models.LocationPoint).filter(
        models.LocationPoint.id==point_id
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
        models.AnimalVisitedLocation.id_location_point == point_id
    )).scalar()

    return any((animals_link, animals_visited_locations_link))


def delete_location_point(db: Session, point_id: int | Column[Integer]):
    db.query(models.LocationPoint).filter(
        models.LocationPoint.id == point_id
    ).delete()
    db.commit()

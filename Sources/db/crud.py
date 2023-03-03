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

from pydantic import EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, exists

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


def exists_account_with_email(db: Session, email: EmailStr | String) -> bool:
    return db.query(exists().where(models.Account.email==email)).scalar()


def get_user(db: Session, email: str) -> models.Account:
    return db.query(models.Account).filter(models.Account.email==email).first()

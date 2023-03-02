from db import models
from models import schemas


def validate_account(account: models.Account) -> schemas.Account:
    return schemas.Account(
        id=account.id,  # type: ignore
        firstName=account.firstName,  # type: ignore
        lastName=account.lastName,  # type: ignore
        email=account.email,  # type: ignore
        password=account.password  # type: ignore
    )
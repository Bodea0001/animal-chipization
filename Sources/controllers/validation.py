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


def validate_location_point(
    location_point: models.LocationPoint
) -> schemas.LocationPoint:
    return schemas.LocationPoint(
        id=location_point.id,  # type: ignore
        latitude=location_point.latitude,  # type: ignore
        longitude=location_point.longitude  # type: ignore
    )

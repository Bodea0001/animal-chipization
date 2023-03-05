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


def validate_animal_type(animal_type: models.AnimalType) -> schemas.AnimalType:
    return schemas.AnimalType(
        id=animal_type.id,  # type: ignore
        type=animal_type.type  # type: ignore
    )


def validate_animal(animal: models.Animal) -> schemas.Animal:
    animal_types = _validate_animal_types(animal.animalTypes)
    visited_locations = _validate_visited_locations(animal.visitedLocations)
    return schemas.Animal(
        id=animal.id,  # type: ignore
        animalTypes=animal_types,
        weight=animal.weight,  # type: ignore
        length=animal.length,  # type: ignore
        height=animal.height,  # type: ignore
        gender=animal.gender,   # type: ignore
        lifeStatus=animal.lifeStatus,  # type: ignore
        chippingDateTime=animal.chippingDateTime,  # type: ignore
        chipperId=animal.chipperId,  # type: ignore
        chippingLocationId=animal.chippingLocationId,  # type: ignore
        visitedLocations=visited_locations,
        deathDateTime=animal.deathDateTime  # type: ignore
    )


def _validate_animal_types(animal_types: list[models.AnimalType]) -> list[int]:
    return [type.id for type in animal_types]  # type: ignore
    

def _validate_visited_locations(
    visited_locations: list[models.AnimalVisitedLocation]
) -> list[int]:
    sorted_visited_locations = sorted(
        visited_locations, 
        key=lambda loc: loc.dateTimeOfVisitLocationPoint  # type: ignore
    )
    return [location.id_location_point for location in sorted_visited_locations]  # type: ignore
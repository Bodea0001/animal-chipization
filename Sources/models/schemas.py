import pytz
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, validator, Field
from fastapi import HTTPException, status

from controllers.mail import is_email_valid


#Role -------------------------------------------------------------------------
class Role(str, Enum):
    USER = "USER"
    CHIPPER = "CHIPPER"
    ADMIN = "ADMIN"
        

# Account ---------------------------------------------------------------------
class AccountBase(BaseModel):
    firstName: str
    lastName: str
    email: str

    class Config:
        orm_mode = True


class AccountRegistration(AccountBase):
    password: str

    @validator("firstName", "lastName", "password", pre=True, always=True)
    def validate_attributes(cls, attribute):
        if not attribute or not attribute.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        return attribute.strip()
    

    @validator("email", pre=True, always=True)
    def validate_email(cls, email):
        if not email or not email.strip() or not is_email_valid(email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        return email


class AccountAdding(AccountRegistration):
    role: Role


class AccountUpdate(AccountRegistration):
    role: Role


class AccountOut(AccountBase):
    id: int
    role: Role


class AccountSearch(AccountBase):
    firstName: str | None
    lastName: str | None
    email: str | None


class Account(AccountRegistration, AccountOut):
    pass


#LocationPoint ----------------------------------------------------------------
class LocationPointBase(BaseModel):
    latitude: float
    longitude: float

    @validator("latitude", pre=True, always=True)
    def validate_latitude(cls, latitude):
        if latitude is None or latitude < -90 or latitude > 90:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        return latitude

    @validator("longitude", pre=True, always=True)
    def validate_longitude(cls, longitude):
        if longitude is None or longitude < -180 or longitude > 180:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        return longitude


class LocationPoint(LocationPointBase):
    id: int


# AnimalTypes -----------------------------------------------------------------
class AnimalTypeBase(BaseModel):
    type: str

    @validator("type", pre=True, always=True)
    def validate_type(cls, type):
        if not type or not type.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        return type


class AnimalType(AnimalTypeBase):
    id: int


#Animal -----------------------------------------------------------------------
class Gender(str, Enum):
    male = "MALE"
    female = "FEMALE"
    OTHER = "OTHER"


class AnimalBase(BaseModel):
    weight: float = Field(gt=0)
    length: float = Field(gt=0)
    height: float = Field(gt=0)
    gender: Gender
    chipperId: int = Field(gt=0)
    chippingLocationId: int = Field(gt=0)


class AnimalTypes(BaseModel):
    animalTypes: list[int]

    @validator("animalTypes", pre=True, always=True)
    def validate_animal_types(cls, animal_types):
        if not animal_types:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        for type_id in animal_types:
            if not type_id or type_id <= 0:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        if len(animal_types) != len(set(animal_types)):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT)
        return animal_types


class AnimalCreation(AnimalBase, AnimalTypes):
    pass


class LifeStatus(str, Enum):
    ALIVE = "ALIVE"
    DEAD = "DEAD"


class AnimalUpdate(AnimalBase):
    lifeStatus: LifeStatus
    deathDateTime: datetime | None

    def __init__(self, **data):
        if data.get('lifeStatus') == LifeStatus.DEAD:
            data['deathDateTime'] = datetime.now(tz=pytz.UTC).replace(microsecond=0)
        super().__init__(**data)


class AnimalSearch(BaseModel):
    startDateTime: datetime | None
    endDateTime: datetime | None
    chipperId: int | None = Field(gt=0)
    chippingLocationId: int | None = Field(gt=0)
    lifeStatus: LifeStatus | None
    gender: Gender | None


class AnimalTypeAnimalUpdate(BaseModel):
    oldTypeId: int = Field(gt=0)
    newTypeId: int = Field(gt=0)


class Animal(AnimalBase, AnimalTypes):
    id: int
    lifeStatus: LifeStatus
    chippingDateTime: datetime
    visitedLocations: list[int]
    deathDateTime: datetime | None


# AnimalVisitedLocation -------------------------------------------------------
class AnimalVisitedLocationSearch(BaseModel):
    startDateTime: datetime | None
    endDateTime: datetime | None


class AnimalVisitedLocationOut(BaseModel):
    id: int
    dateTimeOfVisitLocationPoint: datetime
    locationPointId: int


class AnimalVisitedLocationChange(BaseModel):
    visitedLocationPointId: int = Field(gt=0)
    locationPointId: int = Field(gt=0)
    
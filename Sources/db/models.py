from sqlalchemy import (
    Float,
    Column,
    String,
    Double,
    Integer,
    DateTime,
    BigInteger,
    ForeignKey,
)
from datetime import datetime
from sqlalchemy.orm import relationship, declarative_base

from db.database import engine


Base = declarative_base()


class Account(Base):
    __tablename__ = "account"

    id = Column(Integer, primary_key=True, index=True)
    firstName = Column(String, nullable=False)
    lastName = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)


class Animal(Base):  
    __tablename__ = "animal"
    
    id = Column(BigInteger, primary_key=True, index=True)
    weight = Column(Float, nullable=False)
    length = Column(Float, nullable=False)
    height = Column(Float, nullable=False)
    gender = Column(String(6), nullable=False)
    lifeStatus = Column(String(5), nullable=False)
    chippingDateTime = Column(DateTime, default=datetime.utcnow(), nullable=False)
    chipperId = Column(ForeignKey("account.id"), nullable=False)
    chippingLocationId = Column(ForeignKey("location_point.id"), nullable=False)
    deathDateTime = Column(DateTime)

    animalTypes = relationship("AnimalType", secondary="animalType_animal")
    visitedLocations = relationship("AnimalVisitedLocation")


class AnimalType(Base):
    __tablename__ = "animal_type"
    
    id = Column(BigInteger, primary_key=True, index=True)
    type = Column(String, nullable=False)


class AnimalTypeAnimal(Base):
    __tablename__ = "animalType_animal"

    id_animal = Column(ForeignKey("animal.id"), primary_key=True, index=True)
    id_animal_type = Column(ForeignKey("animal_type.id"), primary_key=True, index=True)


class LocationPoint(Base):
    __tablename__ = "location_point"

    id = Column(BigInteger, primary_key=True, index=True)
    latitude = Column(Double, nullable=False)
    longitude = Column(Double, nullable=False)


class AnimalVisitedLocation(Base):
    __tablename__ = "animal_visited_location"
    
    id_animal = Column(ForeignKey("animal.id"), primary_key=True, index=True)
    id_location_point = Column(
        ForeignKey("location_point.id"),
        primary_key=True, 
        index=True
    ) 


if __name__ == "__main__":
    Base.metadata.create_all(engine)
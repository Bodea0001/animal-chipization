from sqlalchemy.orm import Session
from shapely import Point, Polygon

from db import models
from db.crud import get_animal_types, get_location_point
from models.schemas import TypeAnalytics, AnalyticsGroup


def save_animals_with_vis_loc_in_area(
    animal_ids: set,
    polygon: Polygon,
    visited_locations: list[models.AnimalVisitedLocation] | None
):
    if not visited_locations:
        return
    
    for visited_location in visited_locations:
        location_point: models.LocationPoint = visited_location.location_point
        point = Point(location_point.latitude, location_point.longitude)

        if polygon.intersects(point):
            animal_ids.add(visited_location.id_animal)


def save_animals_with_chip_loc_in_area(
    db: Session,
    animal_ids: set,
    polygon: Polygon,
    animals: list[models.Animal] | None
):
    if not animals:
        return
    
    for animal in animals:  # type: ignore
        location_point = get_location_point(db, animal.chippingLocationId)
        point = Point(location_point.latitude, location_point.longitude)  # type: ignore

        if polygon.intersects(point):
            animal_ids.add(animal.id)


def save_and_sort_animals_with_vis_locs_in_area(
    quantity_animal_ids: set,
    arrived_animal_ids: set,
    gone_animal_ids: set,
    polygon: Polygon,
    visited_locations: list[models.AnimalVisitedLocation] | None
):
    if not visited_locations:
        return

    for visited_location in visited_locations:
        db_location_point: models.LocationPoint = visited_location.location_point
        location_point = Point(db_location_point.latitude, db_location_point.longitude)
        animal_id = visited_location.id_animal

        if animal_id in quantity_animal_ids or animal_id in arrived_animal_ids:
            if not polygon.intersects(location_point):
                quantity_animal_ids.discard(animal_id)
                gone_animal_ids.add(animal_id)
        elif polygon.intersects(location_point):
            arrived_animal_ids.add(animal_id)
            if animal_id not in gone_animal_ids:
                quantity_animal_ids.add(animal_id)


def create_types_analytics(
    db: Session,
    quantity_animal_ids: set,
    arrived_animal_ids: set,
    gone_animal_ids: set,
) -> list[TypeAnalytics]:
    types_analytics = {}
    _create_types_analytics_for_analytics_group(
        db, quantity_animal_ids, types_analytics, AnalyticsGroup.QUANTITY)
    _create_types_analytics_for_analytics_group(
        db, arrived_animal_ids, types_analytics, AnalyticsGroup.ARRIVED)
    _create_types_analytics_for_analytics_group(
        db, gone_animal_ids, types_analytics, AnalyticsGroup.GONE)
    return list(types_analytics.values())


def _create_types_analytics_for_analytics_group(
    db: Session,
    animal_ids: set,
    types_analytics: dict,
    group: AnalyticsGroup
):
    for animal_id in animal_ids:
        animal_types = get_animal_types(db, animal_id)
        for animal_type in animal_types:
            type_analytics = types_analytics.get(
                animal_type.id,
                TypeAnalytics(
                    animalType=animal_type.type,  # type: ignore
                    animalTypeId=animal_type.id  # type: ignore
                )
            )
            match group:
                case AnalyticsGroup.QUANTITY: type_analytics.quantityAnimals += 1
                case AnalyticsGroup.ARRIVED: type_analytics.animalsArrived += 1
                case AnalyticsGroup.GONE: type_analytics.animalsGone += 1
            types_analytics[animal_type.id] = type_analytics

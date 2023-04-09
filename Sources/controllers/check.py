from db import models
from models import schemas
from fastapi import HTTPException, status
from shapely.geometry import Polygon, LineString


def is_point_as_prev_or_next(
    data: schemas.AnimalVisitedLocationChange,
    visited_locations: list[models.AnimalVisitedLocation]
) -> bool:
    if len(visited_locations) <= 1:
        return False
    
    change_index = _get_current_index(data.visitedLocationPointId, visited_locations)
    prev_index, next_index = _get_prev_and_next_index(change_index, len(visited_locations))
    
    for i in (prev_index, next_index):
        if i and visited_locations[i].locationPointId == data.locationPointId:
           return True
    return False


def _get_current_index(
    current_id: int,
    visited_locations: list[models.AnimalVisitedLocation]
) -> int:  # type: ignore
    change_index = 0
    for i in range(len(visited_locations)):
        if visited_locations[i].id == current_id:
            return i  

def _get_prev_and_next_index(index: int, length: int) -> tuple[int | None, int | None]:
    if index == 0:
        return None, index + 1
    elif index == length-1:
        return index - 1, None
    else:
        return index - 1, index + 1


def check_border_intersect_in_polygon(polygon: Polygon):
    boundary = LineString(polygon.exterior.coords)

    segments = [LineString([boundary.coords[i], boundary.coords[i+1]])
                for i in range(len(boundary.coords)-1)]

    for i in range(len(segments)):
        for j in range(i+1, len(segments)):
            if i == 0 and j == len(segments)-1:
                continue
            if segments[i].coords[-1] == segments[j].coords[0]:
                continue
            if segments[i].intersects(segments[j]):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
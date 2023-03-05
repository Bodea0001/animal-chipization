from db import models
from models import schemas


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

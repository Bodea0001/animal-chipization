from shapely.geometry import Polygon

from models import schemas


def get_polygon(coords: list[schemas.Point]) -> Polygon:
    return Polygon([(point.latitude, point.longitude) for point in coords])
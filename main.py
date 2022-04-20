from typing import Tuple

from fastapi import Depends, FastAPI

from core.commons import get_station_and_stops
from core.models import Coordinate, SinglePathResponse
from core.paths import SingleAlternativePathBuilder

app = FastAPI()


def points_query(start: str, final: str):
    lon, lat = tuple(map(float, start.split(",")))
    start = Coordinate(lat=lat, lon=lon)
    lon, lat = tuple(map(float, final.split(",")))
    final = Coordinate(lat=lat, lon=lon)
    return start, final


@app.get("/paths/single", response_model=SinglePathResponse)
def single_paths(points: Tuple[Coordinate, Coordinate] = Depends(points_query)):
    start, final = points

    stations_stops = get_station_and_stops(start, final)
    path_builder = SingleAlternativePathBuilder(start, final, stations_stops)
    paths = path_builder.get_all_possible_paths()
    single_path_response = SinglePathResponse(start=start, final=final, paths=paths)

    return single_path_response

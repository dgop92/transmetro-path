from enum import Enum
from typing import List, Optional, Union

from bson import ObjectId
from pydantic import BaseModel


class Coordinate(BaseModel):
    lat: float
    lon: float

    def to_geo_json_dict(self):
        return {"type": "Point", "coordinates": [self.lon, self.lat]}


class Method(Enum):
    WALK = "Walk"
    ALIMENTADOR = "Alimentador"
    TRONCAL = "Troncal"


class ToType(Enum):
    STOP = "Stop"
    STATION = "Station"
    PLACE = "Place"


# Through


class Through(BaseModel):
    method: Method

    class Config:
        json_encoders = {
            ObjectId: lambda o: str(o),
        }


class ThroughWalk(Through):
    method: Optional[Method] = Method.WALK
    distance: float


class ThroughRoute(Through):
    route_data: dict
    amount_to_arrive: int


# ToSomewhere


class ToSomewhere(BaseModel):
    through: Optional[Union[ThroughWalk, ThroughRoute]]
    data: dict

    class Config:
        json_encoders = {
            ObjectId: lambda o: str(o),
        }


class ToStation(ToSomewhere):
    place_type: Optional[ToType] = ToType.STATION


class ToPlace(ToSomewhere):
    place_type: Optional[ToType] = ToType.PLACE


class ToStop(ToSomewhere):
    place_type: Optional[ToType] = ToType.STOP


def serialize_to_somewhere(t: ToSomewhere):

    print("hola", t)
    if isinstance(t, ToStation):
        return t.json(as_type=ToStation)

    return t.json()


class SinglePathResponse(BaseModel):
    start: Coordinate
    final: Coordinate
    paths: List[List[Union[ToStation, ToStop, ToPlace]]]

    class Config:
        json_encoders = {
            ObjectId: lambda o: str(o),
        }

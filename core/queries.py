from typing import List

from bson.objectid import ObjectId

from config.database import db
from core.models import Coordinate


def get_nearby_stations(coordinate: Coordinate, max_distance: int = 500) -> List[dict]:
    return list(
        db["stations"].aggregate(
            [
                {
                    "$geoNear": {
                        "near": coordinate.to_geo_json_dict(),
                        "maxDistance": max_distance,
                        "spherical": True,
                        "distanceField": "distance",
                    }
                },
                {"$project": {"destinations": 0}},
            ]
        )
    )


def get_station_by_object_id(obj_id: ObjectId):
    return db["stations"].find_one({"_id": obj_id}, {"destinations": 0})


def get_route_by_object_id(obj_id: ObjectId):
    return db["routes"].find_one({"_id": obj_id})


def get_nearby_group_stops(
    coordinate: Coordinate, max_distance: int = 500
) -> List[List]:
    stops_data = db["stops"].aggregate(
        [
            {
                "$geoNear": {
                    "near": coordinate.to_geo_json_dict(),
                    "maxDistance": max_distance,
                    "spherical": True,
                    "distanceField": "distance",
                }
            },
            {"$group": {"_id": "$route", "stops": {"$push": "$$ROOT"}}},
        ]
    )
    return list(map(lambda st: st["stops"], stops_data))


def get_possible_routes_between_station(
    start_station_id: ObjectId, final_station_id: ObjectId
):
    return list(
        db["stations"].aggregate(
            [
                {"$match": {"_id": start_station_id}},
                {"$project": {"destinations": 1, "_id": 0}},
                {"$unwind": {"path": "$destinations"}},
                {"$match": {"destinations.station": final_station_id}},
                {
                    "$lookup": {
                        "from": "routes",
                        "localField": "destinations.route",
                        "foreignField": "_id",
                        "as": "route",
                    }
                },
                {
                    "$project": {
                        "destination_data": "$destinations",
                        "route": {"$arrayElemAt": ["$route", 0]},
                    }
                },
            ]
        )
    )

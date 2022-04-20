import csv
import logging
from collections import defaultdict

import pymongo
from commons import (
    get_database,
    get_location_from_coordinates,
    get_route_data_by_name,
    get_station_data_by_name,
)


def extract_location_of_stop(raw_value):
    raw_coordinates = raw_value[7:-1]
    return get_location_from_coordinates(list(map(float, raw_coordinates.split(" "))))


def get_all_alimentadores_route_names(db):
    aggregate_result = db["routes"].aggregate(
        [
            {"$match": {"type_of_route": "alimentador"}},
            {"$group": {"_id": None, "routes": {"$addToSet": "$name"}}},
        ]
    )
    return list(aggregate_result)[0]["routes"]


def get_route_stops(route_names):
    # headers info
    # route name, stop name, stop sequence, useless, useless, geoData
    route_stops = defaultdict(list)
    with open("data/raw_structure_data/all_stops.csv", encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")

        # skip header
        next(csv_reader)
        for row in csv_reader:
            row_splited = row[0].split(" ")
            route_name = row_splited[0]
            if route_name in route_names:
                route_stops[route_name].append(
                    {
                        "description": row[1],
                        "stop_sequence": row[2],
                        "location": extract_location_of_stop(row[5]),
                    }
                )
    return route_stops


def create_stops(db):

    stop_collection = db["stops"]

    logging.info("Delete old collection")
    stop_collection.delete_many({})

    logging.info("Get alimentadores route names")
    route_names = get_all_alimentadores_route_names(db)

    logging.info("Get route stops")
    route_stops = get_route_stops(route_names)

    stop_documents = []

    for route_name, stops in route_stops.items():
        logging.info(f"Process route {route_name}")

        logging.info(f"Get parent station for {route_name}")
        parent_station_name = stops[0]["description"]
        parent_station_data = get_station_data_by_name(db, parent_station_name)

        if not parent_station_data:
            logging.info(f"Could not find parent station for route {route_name}")
            continue

        logging.info(f"Get route data for {route_name}")
        route_data = get_route_data_by_name(db, route_name)

        number_of_stops = len(stops)

        # For normal stops, first and last stop is a station
        stops_with_out_stations = stops[1:-1]

        # Special case A8-3
        other_parent_stations = []
        if route_name == "A8-3":
            logging.info(f"Process special case for {route_name}")
            psd2 = get_station_data_by_name(db, stops[1]["description"])
            psd3 = get_station_data_by_name(db, stops[2]["description"])
            other_parent_stations.extend([psd2["_id"], psd3["_id"]])
            stops_with_out_stations = stops[3:-3]

        for i, stop in enumerate(stops_with_out_stations, start=1):
            amount_to_arrive = number_of_stops - i
            stop_documents.append(
                {
                    **stop,
                    "amount_to_arrive": amount_to_arrive,
                    "route": route_data["_id"],
                    "parent_station": parent_station_data["_id"],
                    "other_parent_stations": other_parent_stations,
                }
            )

    logging.info("Add documents to stop collection ")
    stop_collection.insert_many(stop_documents)

    logging.info("Create 2d sphere index")
    idx_resp = stop_collection.create_index([("location", pymongo.GEOSPHERE)])
    logging.info(f"Index response: {idx_resp}")


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)

    logging.info("Connect to database")
    db = get_database()

    create_stops(db)

import csv
import json
import logging
from collections import defaultdict

import pymongo
from decouple import config


def get_station_data_by_name(db, name):
    clean_name = name.replace("Est. ", "")
    return db["stations"].find_one({"name": clean_name})


def get_route_data_by_name(db, name):
    return db["routes"].find_one({"name": name})


def get_normal_routes():
    normal_routes = []
    with open(
        "data/raw_structure_data/station_route_names.json", "r", encoding="utf-8"
    ) as route_names_file:
        route_names = json.loads(route_names_file.read())
        normal_routes = route_names["normal_routes"]
    return normal_routes


def get_route_stops():
    # headers info
    # route name, stop name, stop sequence, useless, useless, geoData
    normal_routes = get_normal_routes()
    route_stops = defaultdict(list)
    with open("data/raw_structure_data/all_stops.csv", encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")

        # skip header
        next(csv_reader)
        for row in csv_reader:
            row_splited = row[0].split(" ")
            name = row_splited[0]
            if name in normal_routes:
                route_stops[name].append({"stop_name": row[1], "stop_sequence": row[2]})
    return route_stops


def add_destinations_to_station(db):

    logging.info("Get route stops")
    route_stops = get_route_stops()

    for route_name, route_stations in route_stops.items():
        logging.info(f"Process route {route_name}")

        route_data = get_route_data_by_name(db, route_name)
        route_length = len(route_stations)

        for i in range(route_length):
            destinations = []
            station_name = route_stations[i]["stop_name"]
            starting_station_data = get_station_data_by_name(db, station_name)
            for j in range(i + 1, route_length):
                destination_station_name = route_stations[j]["stop_name"]
                destination_station_data = get_station_data_by_name(
                    db, destination_station_name
                )
                amonut_to_arrive = int(route_stations[j]["stop_sequence"]) - int(
                    route_stations[i]["stop_sequence"]
                )
                destinations.append(
                    {
                        "station": destination_station_data["_id"],
                        "amount_to_arrive": amonut_to_arrive,
                        "route": route_data["_id"],
                    }
                )

            logging.info(f"Updating station's destinations of {station_name}")
            old_destinations = starting_station_data.get("destinations", [])
            starting_station_data["destinations"] = [*old_destinations, *destinations]
            db["stations"].replace_one(
                {"_id": starting_station_data["_id"]}, starting_station_data
            )


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)

    MONGO_URL = config("MONGO_URL")
    DB_NAME = config("DB_NAME")

    logging.info("Connect to database")
    client = pymongo.MongoClient(MONGO_URL)
    db = client[DB_NAME]

    add_destinations_to_station(db)

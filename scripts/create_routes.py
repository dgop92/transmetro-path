import json
import logging

import pymongo
from decouple import config

# TODO: load from file
NORMAL_ROUTES = ["R1", "R2", "S1", "S2", "B1", "B2"]
EXPRESS_ROUTES = ["R10", "R40", "S10", "S40", "B10"]

ALIMENTADOR_TYPE = "alimentador"
TRONCAL_EXPRESS_TYPE = "troncal-express"
TRONCAL_TYPE = "troncal"


def route_data_transformation(route_data, type_of_route):
    return {**route_data, "type_of_route": type_of_route}


# https://www.transmetro.gov.co/api/v1/routes/
def get_routes():
    with open(
        "data/raw_structure_data/routes.json", "r", encoding="utf-8"
    ) as route_names_file:
        return json.loads(route_names_file.read())


def create_station_routes(db):

    route_collection = db["routes"]

    logging.info("Delete old collection")
    route_collection.delete_many({})

    routes = get_routes()

    express_routes = []
    troncal_routes = []
    alimentador_routes = []

    for route in routes:

        route_name = route["name"]

        if route_name[0] == "A" or route_name[0] == "U":
            route["type_of_route"] = ALIMENTADOR_TYPE
            logging.info(f"Adding route {route_name} as {ALIMENTADOR_TYPE}")
            alimentador_routes.append(route)
        elif route_name in NORMAL_ROUTES:
            route["type_of_route"] = TRONCAL_TYPE
            logging.info(f"Adding route {route_name} as {TRONCAL_TYPE}")
            troncal_routes.append(route)
        elif route_name in EXPRESS_ROUTES:
            route["type_of_route"] = TRONCAL_EXPRESS_TYPE
            logging.info(f"Adding route {route_name} as {TRONCAL_EXPRESS_TYPE}")
            express_routes.append(route)

        logging.info(f"Route {route['name']} was ignored")

    logging.info("Save troncal routes")
    route_collection.insert_many(troncal_routes)
    logging.info("Save troncal express routes")
    route_collection.insert_many(express_routes)
    logging.info("Save alimentador routes ")
    route_collection.insert_many(alimentador_routes)


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)

    MONGO_URL = config("MONGO_URL")
    DB_NAME = config("DB_NAME")

    logging.info("Connect to database")
    client = pymongo.MongoClient(MONGO_URL)
    db = client[DB_NAME]

    create_station_routes(db)

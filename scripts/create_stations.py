import json
import logging

import pymongo
from decouple import config


def station_data_transformation(station_data):
    location = {
        "type": "Point",
        "coordinates": list(map(float, station_data["location"])),
    }
    return {**station_data, "location": location}


def create_stations(db):
    station_collection = db["stations"]

    logging.info("Delete old collection")
    station_collection.delete_many({})

    with open(
        "data/raw_structure_data/stations.json", "r", encoding="utf-8"
    ) as station_data_file:
        station_data = json.loads(station_data_file.read())
        transformed_data = map(station_data_transformation, station_data)
        logging.info("Save new documents")
        station_collection.insert_many(transformed_data)

        logging.info("Create 2d sphere index")
        idx_resp = station_collection.create_index([("location", pymongo.GEOSPHERE)])
        logging.info(f"Index response: {idx_resp}")


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)

    MONGO_URL = config("MONGO_URL")
    DB_NAME = config("DB_NAME")

    logging.info("Connect to database")
    client = pymongo.MongoClient(MONGO_URL)
    db = client[DB_NAME]

    create_stations(db)

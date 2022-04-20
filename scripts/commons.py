import pymongo
from decouple import config


def get_station_data_by_name(db, name):
    clean_name = name.replace("Est. ", "")
    return db["stations"].find_one({"name": clean_name})


def get_route_data_by_name(db, name):
    return db["routes"].find_one({"name": name})


def get_location_from_coordinates(coordinates):
    return {
        "type": "Point",
        "coordinates": coordinates,
    }


def get_database():

    MONGO_URL = config("MONGO_URL")
    DB_NAME = config("DB_NAME")

    client = pymongo.MongoClient(MONGO_URL)
    return client[DB_NAME]

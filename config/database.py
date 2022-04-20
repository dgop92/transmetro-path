import pymongo
from decouple import config

MONGO_URL = config("MONGO_URL")
DB_NAME = config("DB_NAME")

client = pymongo.MongoClient(MONGO_URL)
db = client[DB_NAME]

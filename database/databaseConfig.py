import os

from dotenv import find_dotenv, load_dotenv
from pymongo import MongoClient

load_dotenv(find_dotenv())

connectionString = os.environ.get("MONGODB_CONNECTION_STRING")

# Fallback to local MongoDB if connection string is not properly configured
if (
    not connectionString
    or "username:password" in connectionString
    or connectionString == "mongodb+srv://username:password@cluster.mongodb.net/"
):
    print(
        "Warning: MONGODB_CONNECTION_STRING not properly configured, using local MongoDB"
    )
    connectionString = "mongodb://localhost:27017/"

try:
    dbclient = MongoClient(connectionString)
    # Test the connection
    dbclient.admin.command("ping")
    print(f"Successfully connected to MongoDB")
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")
    print("Attempting to connect to local MongoDB as fallback...")
    connectionString = "mongodb://localhost:27017/"
    dbclient = MongoClient(connectionString)
    dbclient.admin.command("ping")
    print("Connected to local MongoDB")

beehive = dbclient.beehive


def get_beehive_user_collection():
    return beehive.users


def get_beehive_image_collection():
    return beehive.images


def get_beehive_admin_collection():
    return beehive.admins


def get_beehive_notification_collection():
    return beehive.notifications


def get_beehive_message_collection():
    return beehive.messages

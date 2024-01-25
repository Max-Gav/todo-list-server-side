from pymongo import MongoClient
import os

def connectToDatabase(app):
    app.mongodb_client = MongoClient(os.getenv("MONGODB_URI"))
    app.database = app.mongodb_client[os.getenv("DB_NAME")]
    print("Connected to the MongoDB database!")

def disconnectFromDatabase(app):
    app.mongodb_client.close()

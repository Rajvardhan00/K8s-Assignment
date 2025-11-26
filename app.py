from flask import Flask, request, jsonify
from pymongo import MongoClient
import os
from datetime import datetime

app = Flask(__name__)

MONGO_HOST = os.environ.get("MONGO_HOST", "mongodb")
MONGO_PORT = os.environ.get("MONGO_PORT", "27017")

client = MongoClient(f"mongodb://{MONGO_HOST}:{MONGO_PORT}/")
db = client["flask_db"]
collection = db.data

@app.route("/")
def home():
    return f"Welcome! Time now: {datetime.now()}"

@app.route("/data", methods=["GET", "POST"])
def data():
    if request.method == "POST":
        body = request.get_json()
        collection.insert_one(body)
        return jsonify({"msg": "Inserted"}), 201
    else:
        result = list(collection.find({}, {"_id": 0}))
        return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

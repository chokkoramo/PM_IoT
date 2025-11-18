import os
from datetime import datetime
from flask import Flask, jsonify, request
from pymongo import MongoClient
from pymongo.errors import PyMongoError

app = Flask(__name__)

mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)

db_name = os.environ.get('MONGO_DB', 'test')
db = client[db_name]
coll = db['data']


@app.route('/')
def home():
    return "OK", 200


@app.route('/search', methods=['POST'])
def search():
    try:
        sensors = coll.distinct('data')
        return jsonify(sensors)
    except Exception:
        return jsonify([])


@app.route('/query', methods=['POST'])
def query():
    try:
        req = request.get_json(force=True)
        targets = req.get('targets', [])
        range_ = req.get('range', {})

        from_ts = datetime.fromisoformat(range_['from'].replace("Z", "+00:00"))
        to_ts = datetime.fromisoformat(range_['to'].replace("Z", "+00:00"))

        response = []

        for t in targets:
            sensor_name = t.get("target")

            query = {
                "sensor": sensor_name,
                "ts": {"$gte": from_ts, "$lte": to_ts}
            }

            cursor = coll.find(query).sort("ts", 1)

            datapoints = []
            for d in cursor:
                val = d.get("value")
                ts = d.get("ts")
                if hasattr(ts, "timestamp"):
                    datapoints.append([val, int(ts.timestamp() * 1000)])

            response.append({
                "target": sensor_name,
                "datapoints": datapoints
            })

        return jsonify(response)

    except Exception as e:
        print("Query Error:", e)
        return jsonify([])


@app.route('/json_api_data', methods=['POST', 'GET'])
def json_api_data():
    try:
        req = request.get_json(force=True)
        sensor = req.get("sensor")
        limit = int(req.get("limit", 50))

        query = {"sensor": sensor} if sensor else {}

        cursor = coll.find(query).sort("ts", -1).limit(limit)

        data = []
        for d in cursor:
            d["_id"] = str(d["_id"])
            if hasattr(d["ts"], "isoformat"):
                d["ts"] = d["ts"].isoformat()
            data.append(d)

        return jsonify({"ok": True, "count": len(data), "data": data})

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


@app.route('/receive_sensor_data', methods=['POST'])
def receive_sensor_data():
    payload = request.get_json(silent=True)

    if not payload or "value" not in payload:
        return jsonify({"ok": False, "error": "Invalid JSON"}), 400

    try:
        ts = payload.get("ts")

        if isinstance(ts, str):
            try:
                ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except:
                ts = datetime.utcnow()
        elif ts is None:
            ts = datetime.utcnow()

        doc = {
            "sensor": payload.get("sensor"),
            "value": payload.get("value"),
            "unit": payload.get("unit"),
            "ts": ts
        }

        res = coll.insert_one(doc)
        return jsonify({"ok": True, "id": str(res.inserted_id)}), 201

    except PyMongoError as e:
        return jsonify({"ok": False, "error": str(e)}), 503


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7001)
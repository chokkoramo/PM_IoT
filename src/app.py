import os
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
from pymongo.errors import PyMongoError

app = Flask(__name__)

def get_mongo_client():
    """
    Devuelve un cliente MongoDB.
    Prioriza MONGO_URL (Atlas) y si no existe, usa configuración local.
    """
    mongo_url = os.environ.get('MONGO_URL')
    if mongo_url:
        return MongoClient(mongo_url, serverSelectionTimeoutMS=5000)

    host = os.environ.get('MONGO_HOST', 'mongo')
    port = os.environ.get('MONGO_PORT', '27017')
    user = os.environ.get('MONGO_USER')
    password = os.environ.get('MONGO_PASSWORD')

    if user and password:
        uri = f"mongodb://{user}:{password}@{host}:{port}/?authSource=admin"
    else:
        uri = f"mongodb://{host}:{port}/"

    return MongoClient(uri, serverSelectionTimeoutMS=5000)


@app.route('/')
def home():
    return jsonify({
        "ok": True,
        "message": "API Flask + MongoDB Atlas funcionando correctamente"
    })


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/api/send', methods=['POST'])
def send_data():
    """
    Recibe un JSON y guarda el documento en MongoDB.
    Ejemplo:
    {
      "sensor": "temperatura",
      "value": 24.5,
      "meta": {"ubicacion": "sala"}
    }
    """
    data = request.get_json(silent=True)
    if not data or 'value' not in data:
        return jsonify({'ok': False, 'error': 'Se requiere un campo "value" en el JSON.'}), 400

    try:
        client = get_mongo_client()
        db_name = os.environ.get('MONGO_DB', 'test')
        db = client[db_name]
        coll = db['data']

        doc = {
            'sensor': data.get('sensor'),
            'value': data.get('value'),
            'meta': data.get('meta'),
            'ts': datetime.utcnow()
        }

        res = coll.insert_one(doc)
        return jsonify({'ok': True, 'inserted_id': str(res.inserted_id)}), 201

    except PyMongoError as e:
        return jsonify({'ok': False, 'error': str(e)}), 503


# === MAIN ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7001, debug=True)

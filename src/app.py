import os
import socket
from datetime import datetime
from flask import Flask, render_template, jsonify, request

from pymongo import MongoClient
from pymongo.errors import PyMongoError

app = Flask(__name__)


def get_mongo_client():
    """
    Preferir MONGO_URL si está definido (p. ej. Atlas).
    Si no, construir URI a partir de host/port/user/password manejando valores vacíos.
    """
    mongo_url = os.environ.get('MONGO_URL')
    if mongo_url:
        # Si usas Atlas es recomendable usar el URI "mongodb+srv://..."
        return MongoClient(mongo_url, serverSelectionTimeoutMS=5000)

    host = os.environ.get('MONGO_HOST', 'mongo')
    port = os.environ.get('MONGO_PORT')
    user = os.environ.get('MONGO_USER')
    password = os.environ.get('MONGO_PASSWORD')

    # validar port
    port_int = None
    if port:
        try:
            port_int = int(port)
        except Exception:
            port_int = None

    # construir URI seguro
    if user and password:
        # si el host es un SRV host (Atlas) y no trae puerto, puede fallar — mejor usar MONGO_URL
        if port_int:
            uri = f"mongodb://{user}:{password}@{host}:{port_int}/?authSource=admin"
        else:
            uri = f"mongodb://{user}:{password}@{host}/?authSource=admin"
    else:
        if port_int:
            uri = f"mongodb://{host}:{port_int}/"
        else:
            uri = f"mongodb://{host}/"

    return MongoClient(uri, serverSelectionTimeoutMS=5000)


@app.route('/')
def home():
    return "Hello, Flask!"


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/api/data', methods=['POST'])
def api_insert_data():
    """
    Espera JSON: {"sensor": "nombre", "value": 123, "ts": "2025-10-30T12:00:00Z" (opcional)}
    Inserta en la colección 'data' y devuelve el id insertado.
    """
    payload = request.get_json(silent=True)
    if not payload or 'value' not in payload:
        return jsonify({'ok': False, 'error': 'JSON required with at least "value" field'}), 400

    try:
        client = get_mongo_client()
        db_name = os.environ.get('MONGO_DB', 'test')
        db = client[db_name]
        coll = db['data']
        doc = {
            'sensor': payload.get('sensor'),
            'value': payload.get('value'),
            'meta': payload.get('meta'),
            'ts': payload.get('ts') or datetime.utcnow()
        }
        res = coll.insert_one(doc)
        return jsonify({'ok': True, 'inserted_id': str(res.inserted_id)}), 201
    except PyMongoError as e:
        return jsonify({'ok': False, 'error': str(e)}), 503


@app.route('/api/data', methods=['GET'])
def api_list_data():
    """
    Lista documentos recientes. Parámetros opcionales:
    - limit: número de documentos (por defecto 20)
    - sensor: filtrar por sensor
    """
    try:
        limit = int(request.args.get('limit', 20))
    except ValueError:
        limit = 20

    sensor = request.args.get('sensor')

    try:
        client = get_mongo_client()
        db_name = os.environ.get('MONGO_DB', 'test')
        db = client[db_name]
        coll = db['data']

        query = {}
        if sensor:
            query['sensor'] = sensor

        docs_cursor = coll.find(query).sort('ts', -1).limit(limit)
        docs = []
        for d in docs_cursor:
            d['_id'] = str(d.get('_id'))
            ts = d.get('ts')
            if hasattr(ts, 'isoformat'):
                d['ts'] = ts.isoformat()
            docs.append(d)

        return jsonify({'ok': True, 'count': len(docs), 'data': docs}), 200
    except PyMongoError as e:
        return jsonify({'ok': False, 'error': str(e)}), 503


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7001, debug=True)

import os
import socket
from datetime import datetime
from flask import Flask, render_template, jsonify, request

from pymongo import MongoClient
from pymongo.errors import PyMongoError

app = Flask(__name__)


def get_mongo_client():
    host = os.environ.get('MONGO_HOST', 'mongo')
    port = int(os.environ.get('MONGO_PORT', '27017'))
    user = os.environ.get('MONGO_USER')
    password = os.environ.get('MONGO_PASSWORD')
    if user and password:
        uri = f"mongodb://{user}:{password}@{host}:{port}/?authSource=admin"
    else:
        uri = f"mongodb://{host}:{port}/"
    return MongoClient(uri, serverSelectionTimeoutMS=2000)


@app.route('/')
def home():
    return "Hello, Flask!"


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/insert-test', methods=['GET', 'POST'])
def insert_test():
    val = None
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        val = data.get('value')
    if val is None:
        val = request.args.get('value')
    if val is None:
        return jsonify({'ok': False, 'error': 'missing `value` parameter (query or JSON body)'}), 400

    try:
        client = get_mongo_client()
        db_name = os.environ.get('MONGO_DB', 'test')
        db = client[db_name]
        coll = db['test_collection']
        doc = {'value': val, 'ts': datetime.utcnow()}
        res = coll.insert_one(doc)
        return jsonify({'ok': True, 'inserted_id': str(res.inserted_id)}), 201
    except PyMongoError as e:
        return jsonify({'ok': False, 'error': str(e)}), 503


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7001, debug=True)

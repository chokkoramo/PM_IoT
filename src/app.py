import os
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
from pymongo.errors import PyMongoError

app = Flask(__name__)

mongo_url = os.environ.get('MONGO_URL', 'mongodb://mongo/')
client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
db_name = os.environ.get('MONGO_DB', 'test')
db = client[db_name]
coll = db['data']


@app.route('/')
def home():
    return "Hello, Flask!"


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/test-form')
def test_form():
    return render_template('test_form.html')


@app.route('/api/data', methods=['POST'])
def api_insert_data():
    payload = request.get_json(silent=True)
    if not payload or 'value' not in payload:
        return jsonify({'ok': False, 'error': 'JSON required with at least "value" field'}), 400

    try:
        doc = {
            'sensor': payload.get('sensor'),
            'value': payload.get('value'),
            'ts': payload.get('ts') or datetime.utcnow()
        }
        res = coll.insert_one(doc)
        return jsonify({'ok': True, 'inserted_id': str(res.inserted_id)}), 201
    except PyMongoError as e:
        return jsonify({'ok': False, 'error': str(e)}), 503


@app.route('/api/data', methods=['GET'])
def api_list_data():
    try:
        limit = int(request.args.get('limit', 20))
    except ValueError:
        limit = 20

    sensor = request.args.get('sensor')

    try:
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

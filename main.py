import json
import traceback

from flask import Flask, jsonify
from flask import request
from LFGParser import parse_json
from flask import make_response

app = Flask(__name__, )


@app.route('/parse_lfg', methods=['OPTIONS'])
def allowall():
    resp = make_response()
    h = resp.headers
    h['Access-Control-Allow-Origin'] = "*"
    h['Access-Control-Allow-Methods'] = 'POST'
    h['Access-Control-Allow-Headers'] = 'content-type'
    return resp


@app.route('/parse_lfg', methods=['POST'])
def parse_lfg():
    result = {"status": "success", "data": "unknown error"}
    try:
        data = request.data.decode('utf-8')
        print data
        json_object = json.loads(data)
        result = {"status": "success", "data": parse_json(json_object)}
    except Exception as e:
        traceback.print_exc()
        result = {"status": "error", "data": "{}: {}".format(e.__class__.__name__, e.message)}
    finally:
        resp =  jsonify(**result)
        h = resp.headers
        h['Access-Control-Allow-Origin'] = "*"
        h['Access-Control-Allow-Methods'] = 'POST'
        h['Access-Control-Allow-Headers'] = 'content-type'
        return resp

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

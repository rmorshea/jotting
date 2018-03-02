from flask import Flask, jsonify, request
from jotting import book
import json

# Server
# ------

app = Flask(__name__)


@app.route("/api/task", methods=["PUT"])
def task():
    data = json.loads(request.data)
    with book('api', data["parent"]):
        book.conclude(status=200)
        return jsonify({"status": 200})


# Client
# ------

with book('put') as b:
    route = '/api/task'
    data = json.dumps({'parent': b.tag})
    app.test_client().put(route, data=data)

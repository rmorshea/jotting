from flask import Flask, jsonify
from jotting import book

# Server
# ------

app = Flask(__name__)


@app.route("/api/<string:task>")
def index(task):
    with book('api', task):
        book.close(status=200)
        return jsonify({"status": 200})


# Client
# ------

with book('get') as b:
    app.test_client().get('/api/%s' % b.tag)

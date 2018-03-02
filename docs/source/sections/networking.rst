Networking
==========

We've covered a lot of use cases, but we can go even further. In the real world
we aren't working with single `threads`_, `processes`_, or `services`_. Modern
systems are asynchronous and distributed. Following the causes and effects within
these systems quickly becomes impossible. However with `jotting`, it's possible
to begin a `book` using the `tag` of a parent task that triggered it. In this way
logs can be linked across any context. We can build a very simple `Flask` app
to demonstrate how we might link a book between a client and server:

.. code-block:: python

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

.. code-block:: text

    |-- started: get
    |   @ 2018-02-25 18:22:45.912632
    |   |-- started: api
    |   |   @ 2018-02-25 18:22:45.922958
    |   |   `-- success: api
    |   |       @ 2018-02-25 18:22:45.923105
    |   |       | status: 200
    |   |       | duration: 0.000 seconds
    |   `-- success: get
    |       @ 2018-02-25 18:22:45.928721
    |       | duration: 0.016 seconds

.. External Links
.. ==============

.. _threads: https://github.com/rmorshea/jotting/blob/master/examples/threads.py
.. _processes: https://github.com/rmorshea/jotting/blob/master/examples/processes.py
.. _services: https://github.com/rmorshea/jotting/blob/master/examples/services.py

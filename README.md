# Jotting

[![Documentation Status](https://readthedocs.org/projects/jotting/badge/?version=latest)](http://jotting.readthedocs.io/en/latest/?badge=latest)

Logs that explain when, where, and why things happen.

> Jotting was heavily inspired by [`eliot`](https://eliot.readthedocs.io/).

`jotting` is a log system for Python 2 and 3 that can be used to record the causal history of an asynchronous or distributed system. These histories are composed of actions which, once "started", will begin "working", potentially spawn other actions, and eventually end as a "success" or "failure". In the end you're left with a breadcrumb trail of information that you can use to squash bugs with minimal boilerplate.

# Quickstart

Install `jotting` with `pip`:

```bash
$ pip install jotting
```

Then `requests` and `flask` to follow along with the examples:

```bash
$ pip install requests flask
```

## Bookmarking

We'll start with a function that uses `requests` to return a response from a url:

```python
import requests


def get_url(url):
    r = requests.get(url)
    r.raise_for_status()
    return r


response = get_url("https://google.com")
```

Then we'll start logging what it does by adding a `book.mark` decorator:

```python
import requests
from jotting import book


@book.mark
def get_url(url):
    r = requests.get(url)
    r.raise_for_status()
    return r


response = get_url("https://google.com")
```

Once we've done this we'll immediately begin to see printed log statements:

```
|-- started: __main__.get_url
|   @ 2018-01-14 17:08:19.223383
|   | url: https://google.com
|   `-- success: __main__.get_url
|       @ 2018-01-14 17:08:20.101563
|       | returned: <Response [200]>
|       | duration: 0.879 seconds
```

But if we need more information than this we can also use `book.write`:

```python
import requests
from jotting import book


@book.mark
def get_url(url):
    r = requests.get(url)
    book.write(debug="checking status...")
    r.raise_for_status()
    return r


response = get_url("https://google.com")
```

And now we get an extra log telling us what's going on inside `get_url`:

```
|-- started: __main__.get_url
|   @ 2018-01-14 17:08:19.223383
|   | url: https://google.com
|   |-- working: __main__.get_url
|   |   @ 2018-01-14 17:08:20.101401
|   |   | debug: checking status...
|   `-- success: __main__.get_url
|       @ 2018-01-14 17:08:20.101563
|       | returned: <Response [200]>
|       | duration: 0.879 seconds
```

## Putting Things In Context

But wait! We have scripts or functions that have subtasks we'd like to monitor:

```python
import requests

urls = ("https://google.com", "not-here")

responses = []
for u in urls:
    r = requests.get(u)
    r.raise_for_status()
    responses.append(r)
```

We can use the `book` context to define actions that exist independently of functions:

```python
import requests
from jotting import book

urls = ("https://google.com", "not-here")

responses = []
for u in urls:
    with book("getting %s" % u):
        r = requests.get(u)
        r.raise_for_status()
        responses.append(r)
```

This will produce just the kind of fine grained logs we need:

```
|-- started: getting https://google.com
|   @ 2018-01-14 17:06:22.016731
|   `-- success: getting https://google.com
|       @ 2018-01-14 17:06:23.006855
|       | duration: 0.990 seconds
|-- started: getting not-here
|   @ 2018-01-14 17:06:23.007092
|   `-- failure: getting not-here
|       @ 2018-01-14 17:06:23.007587
|       | MissingSchema: Invalid URL 'not-here': No schema supplied. Perhaps you meant http://not-here?
|       | duration: 0.001 seconds
```

# Stashing Outputs

Under the hood, `jotting` creates json encoded messages that contain the information
required to reconstruct a history of actions. If we need to reconfigure where and/or
how `jotting` logs, we choose new outlets and styles. In a case where we want to
print terse logs to sdtout, but save raw json blobs to a file for later consumption,
we can use a `Log` styled `Print` outlet and a `Raw` styled `File` outlet respectively.
For the `Log` style, only the successes and failures of logs where a title has been
given are reported - thus we will title our `book.mark` with something explanatory:

```python
import requests
from jotting import book, to, style

to_print = to.Print(style.Log())
to_file = to.File(path="~/Desktop/logbox.txt")
book.distribute(to_print, to_file)


# we can format the title with
# the inputs of the function
@book.mark("getting {url}")
def get_url(url):
    r = requests.get(url)
    r.raise_for_status()
    return r


response = get_url("https://google.com")
```

Now we will find that we got a print out like this:

```
2018-02-21 19:46:03.156873 SUCCESS getting https://google.com after 0.315 seconds - returned: <Response [200]>
```

Along with a `logbox.txt` file on our desktop with the following contents:

```json
{"metadata": {"title": "getting https://google.com", "timestamps": [1519971599.449055], "tag": "69a6dbbc015a4eacb007b60012034e45", "parent": "https://google.com", "status": "started", "depth": 0}, "content": {"url": "https://google.com"}}
{"metadata": {"title": "getting https://google.com", "timestamps": [1519971599.449055, 1519971599.898956], "tag": "69a6dbbc015a4eacb007b60012034e45", "parent": "https://google.com", "status": "success", "stop": 1519971599.898953, "depth": 0}, "content": {"returned": "<Response [200]>"}}
```

# Distributed Systems

We've covered a lot of use cases, but we can go even further. In the real world
we aren't working with single [threads](https://github.com/rmorshea/jotting/blob/master/examples/threads.py), [processes](https://github.com/rmorshea/jotting/blob/master/examples/processes.py), or [services](https://github.com/rmorshea/jotting/blob/master/examples/services.py). Modern systems
are asynchronous and distributed. Following the causes and effects within these
systems quickly becomes impossible. However with `jotting`, it's possible to
begin a `book` using the `tag` of a parent task that triggered it. In this way
logs can be linked across any context. We can build a very simple `Flask` app
to demonstrate how we might link a book between a client and server:

```python
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
```

```
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
```

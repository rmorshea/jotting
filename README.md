# Jotting

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
{"metadata": {"tag": "ca5d60ee174111e8b6348c8590280283-0", "depth": 0, "start": 1519243197.023079, "status": "started", "parent": null, "title": "getting https://google.com"}, "content": {"url": "https://google.com"}, "timestamp": 1519243197.023083}
{"metadata": {"tag": "ca5d60ee174111e8b6348c8590280283-0", "depth": 0, "start": 1519243197.023079, "status": "success", "parent": null, "title": "getting https://google.com", "stop": 1519243197.5876129}, "content": {"returned": "<Response [200]>"}, "timestamp": 1519243197.587616}
```

# Distributed Systems

We've covered a lot of use cases, but we can go even further. In the real world
we aren't working with single threads, processes, or machines. Modern systems
are asynchronous and distributed. Following the causes and effects within these
systems quickly becomes impossible. However with `jotting`, it's possible to
begin a `book` using the `tag` of a parent task that triggered it:

*Note that threads are supported without the need to pass a `tag`*

```python
import sys
if sys.version_info < (3, 0):
    from Queue import Queue
else:
    from queue import Queue
import threading, requests
from jotting import book, to, read

book.distribute(to.File(path="~/Desktop/logbox.txt"))


def get(queue, url):
    queue.put(requests.get(url).status_code)


@book.mark
def schedule(function, *args):
    q = Queue()
    for x in args:
        title = "%s(%r)" % (function.__name__, x)
        mark = book.mark(title, book.current().tag)
        threading.Thread(target=mark(function), args=(q, x)).start()
    return [q.get(timeout=5) for i in range(len(args))]


schedule(get, "https://google.com", "https://wikipedia.org")
```

```
|-- started: __main__.schedule
|   @ 2018-02-23 14:56:49.190212
|   | function: <function get at 0x10f1e5ae8>
|   | args: ['https://google.com', 'https://wikipedia.org']
|   |-- started: get('https://google.com')
|   |   @ 2018-02-23 14:56:49.191288
|   |   | queue: <queue.Queue object at 0x10fab8e80>
|   |   | url: https://google.com
|   |   `-- success: get('https://google.com')
|   |       @ 2018-02-23 14:56:49.518117
|   |       | returned: None
|   |       | duration: 0.327 seconds
|   |-- started: get('https://wikipedia.org')
|   |   @ 2018-02-23 14:56:49.192486
|   |   | queue: <queue.Queue object at 0x10fab8e80>
|   |   | url: https://wikipedia.org
|   |   `-- success: get('https://wikipedia.org')
|   |       @ 2018-02-23 14:56:49.412165
|   |       | returned: None
|   |       | duration: 0.220 seconds
|   `-- success: __main__.schedule
|       @ 2018-02-23 14:56:49.518363
|       | returned: [200, 200]
|       | duration: 0.328 seconds
```

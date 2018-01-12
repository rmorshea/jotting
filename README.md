# Jotting

Logs that explain when, where, and why things happen.

> Jotting was heavily inspired by [`eliot`](https://eliot.readthedocs.io/).

`jotting` is a log system for Python 3 that can be used to record the causal history of an asynchronous or distributed system. These histories are composed of actions which, once "started", will begin "working", potentially spawn other actions, and eventually end as a "success" or "failure". In the end you're left with a breadcrumb trail of information that you can use to squash bugs with minimal boilerplate.

# Quickstart

Install `jotting` with `pip`:

```bash
$ pip install jotting
```

Then `requests` to follow the examples:

```bash
$ pip install requests
```

## Bookmaking

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
|   @ 2018-01-08 23:12:55.418166
|   | url: https://google.com
|   `-- success: __main__.get_url
|       @ 2018-01-08 23:12:55.874860
|       | returned: <Response [200]>
```

But if we need more information than we get from `book.mark` we can use `book.write` too:

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
|   @ 2018-01-08 23:17:08.982055
|   | url: https://google.com
|   |-- working: __main__.get_url
|   |   @ 2018-01-08 23:17:09.296040
|   |   | debug: checking status...
|   `-- success: __main__.get_url
|       @ 2018-01-08 23:17:09.296150
|       | returned: <Response [200]>
```

## Putting Things In Context

But wait! We have larger functions that have subtasks we'd like to monitor:

```python
import requests


def get_urls(*urls):
    responses = []
    for u in urls:
        r = requests.get(u)
        r.raise_for_status()
        responses.append(r)
    return response


response = get_urls("https://google.com", "not-here")
```

We can use the `book` context to define actions that exist independently of functions:

```python
import requests
from jotting import book


@book.mark
def get_urls(*urls):
    responses = []
    for u in urls:
        with book("getting %s" % u):
            r = requests.get(u)
            book.write(debug="checking status...")
            r.raise_for_status()
            responses.append(r)
    return response


response = get_urls("https://google.com", "not-here")
```

This will produce just the kind of fine grained logs we need:

```
|-- started: __main__.get_urls
|   @ 2018-01-08 23:36:35.423526
|   | urls: ['bad-url']
|   |-- started: getting 'https://google.com'
|   |   @ 2018-01-08 23:36:35.423667
|   |   |-- working: getting 'https://google.com'
|   |   |   @ 2018-01-08 23:36:35.745160
|   |   |   | debug: checking status...
|   |   `-- success: getting 'https://google.com'
|   |       @ 2018-01-08 23:36:35.745253
|   |-- started: getting 'bad-url'
|   |   @ 2018-01-08 23:36:35.745774
|   |   `-- failure: getting 'bad-url'
|   |       @ 2018-01-08 23:36:35.747312
|   |       | ValueError: bad-url
|   `-- failure: __main__.get_urls
|       @ 2018-01-08 23:36:35.747589
|       | ValueError: bad-url
```

# Bookkeeping

Under the hood, `jotting` creates json encoded messages that contain the information
required to reconstruct a history of actions. If we want to reconfigure where and/or
how `jotting` logs, we can change the "writer" of `book`.

```python
import requests
from jotting import book, dist, style, write

to_file = dist.ToFile("~/Desktop/logbox.txt", style=style.Tree())
book.edit(writer=write.thread.Writer(to_file))


@book.mark
def get_url(url):
    r = requests.get(url)
    r.raise_for_status()
    return r


response = get_url("https://google.com")
```

We can view the raw logs by sending them directly to `stdout`:

```python
import sys
import requests
from jotting import book

book.edit(writer=sys.stdout.write)


@book.mark
def get_url(url):
    r = requests.get(url)
    r.raise_for_status()
    return r


response = get_url("https://google.com")
```

Which end up looking like this:

```
{"metadata": {"title": "__main__.get_url", "tag": "1e581186-f513-11e7-8507-c82a142de70e", "status": "started", "parent": null, "timestamp": 1515484812.1124601}, "content": {"url": "https://google.com"}}
{"metadata": {"title": "__main__.get_url", "tag": "1e581186-f513-11e7-8507-c82a142de70e", "status": "success", "parent": null, "timestamp": 1515484812.836246}, "content": {"returned": "<Response [200]>"}}
```

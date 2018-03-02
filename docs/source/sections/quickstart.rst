Quickstart
==========

We'll start with a function that uses `requests` to return a response from a url:

.. code-block:: python

    import requests


    def get_url(url):
        r = requests.get(url)
        r.raise_for_status()
        return r


    response = get_url("https://google.com")

Then we'll start logging what it does by adding a `book.mark` decorator:

.. code-block:: python

    import requests
    from jotting import book


    @book.mark
    def get_url(url):
        r = requests.get(url)
        r.raise_for_status()
        return r


    response = get_url("https://google.com")

Once we've done this we'll immediately begin to see printed log statements:

.. code-block:: text

    |-- started: __main__.get_url
    |   @ 2018-01-14 17:08:19.223383
    |   | url: https://google.com
    |   `-- success: __main__.get_url
    |       @ 2018-01-14 17:08:20.101563
    |       | returned: <Response [200]>
    |       | duration: 0.879 seconds

But if we need more information than this we can also use `book.write`:

.. code-block:: python

    import requests
    from jotting import book


    @book.mark
    def get_url(url):
        r = requests.get(url)
        book.write(debug="checking status...")
        r.raise_for_status()
        return r


    response = get_url("https://google.com")

And now we get an extra log telling us what's going on inside `get_url`:

.. code-block:: text

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

Putting Things In Context
-------------------------

But wait! We have scripts or functions that have subtasks we'd like to monitor:

.. code-block:: python

    import requests

    urls = ("https://google.com", "not-here")

    responses = []
    for u in urls:
        r = requests.get(u)
        r.raise_for_status()
        responses.append(r)

We can use the `book` context to define actions that exist independently of functions:

.. code-block:: python

    import requests
    from jotting import book

    urls = ("https://google.com", "not-here")

    responses = []
    for u in urls:
        with book("getting %s" % u):
            r = requests.get(u)
            r.raise_for_status()
            responses.append(r)

This will produce just the kind of fine grained logs we need:

.. code-block:: text

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

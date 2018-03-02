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

In the following section we will see how to save logs to files.

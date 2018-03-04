Styling Logs
============

In the last section we saw how to save logs to files, and we also noticed, that
under the hood, each log message was actually a dictionary of data. Yet we know
that ``jotting`` can produce human readable readouts. This is possible by
"styling" log statements - reformatting the raw data into a more presentable form.
Each :class:`jotting.to.Outlet` accepts as its first argument, and style - a
callable object which, given raw log data, returns a formatted string. The
default style for outlets is :class:`jotting.style.Raw` which simply encodes the
data as a json blob, but we could also use :class:`jotting.style.Tree` to produce
nested ascii readouts instead:

.. code-block:: python

    import requests
    from jotting import book, to, style

    tree = style.Tree()
    path = "~/Desktop/logbox.txt"
    tree_to_file = to.File(tree, path=path)
    book.distribute(tree_to_file)


    @book.mark("getting {url}")
    def get_url(url):
        r = requests.get(url)
        r.raise_for_status()
        return r


    response = get_url("https://google.com")

Now instead of raw log data, we'll find an ascii tree in ``logbox.txt``:

.. code-block:: text

    |-- started: getting https://google.com
    |   @ 2018-03-03 16:53:45.380436
    |   | url: https://google.com
    |   `-- success: getting https://google.com
    |       @ 2018-03-03 16:53:45.692461
    |       | returned: <Response [200]>
    |       | duration: 0.312 seconds

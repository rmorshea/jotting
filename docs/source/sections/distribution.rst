Distribution
============

Under the hood, `jotting` creates json encoded messages that contain the information
required to reconstruct a history of actions. If we need to reconfigure where and/or
how `jotting` logs, we choose new outlets and styles. In a case where we want to
print terse logs to sdtout, but save raw json blobs to a file for later consumption,
we can use a `Log` styled `Print` outlet and a `Raw` styled `File` outlet respectively.
For the `Log` style, only the successes and failures of logs where a title has been
given are reported - thus we will title our `book.mark` with something explanatory:

.. code-block:: python

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

Now we will find that we got a print out like this:

.. code-block:: text

    2018-02-21 19:46:03.156873 SUCCESS getting https://google.com after 0.315 seconds - returned: <Response [200]>

Along with a `logbox.txt` file on our desktop with the following contents:

.. code-block:: text

    {"metadata": {"title": "getting https://google.com", "timestamps": [1519973286.701371], "tag": "d6154a2a16db4561b151fc43b3781f75", "parent": null, "status": "started", "depth": 0}, "content": {"url": "https://google.com"}}
    {"metadata": {"title": "getting https://google.com", "timestamps": [1519973286.701371, 1519973286.991931], "tag": "d6154a2a16db4561b151fc43b3781f75", "parent": null, "status": "success", "stop": 1519973286.991928, "depth": 0}, "content": {"returned": "<Response [200]>"}}

We can then read each line back as a json blob, and print things out cleanly:

.. code-block:: text

    [
      {
        "metadata": {
          "title": "getting https://google.com",
          "timestamps": [
            1519973286.701371
          ],
          "tag": "d6154a2a16db4561b151fc43b3781f75",
          "parent": null,
          "status": "started",
          "depth": 0
        },
        "content": {
          "url": "https://google.com"
        }
      },
      {
        "metadata": {
          "title": "getting https://google.com",
          "timestamps": [
            1519973286.701371,
            1519973286.991931
          ],
          "tag": "d6154a2a16db4561b151fc43b3781f75",
          "parent": null,
          "status": "success",
          "stop": 1519973286.991928,
          "depth": 0
        },
        "content": {
          "returned": "<Response [200]>"
        }
      }
    ]

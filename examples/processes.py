import sys
import time
import threading, requests
from jotting import book, to, read
from multiprocessing import Process, Queue

logbox = "~/Desktop/logbox.txt"
book.distribute(to.File(path=logbox))


def get(queue, url, parent):
    """Get the URL and queue the response."""
    book.distribute(to.File(path=logbox))
    with book("get({url})", parent, url=url):
        try:
            response = requests.get(url)
        except Exception as e:
            queue.put(e)
        else:
            queue.put(response.status_code)


@book.mark
def schedule(function, *args):
    """Create a process for each mapping of the function to args."""
    q = Queue()
    for x in args:
        # we want to resume the current book
        inputs = (q, x, book.current("tag"))
        Process(target=function, args=inputs).start()
        book.write(scheduled=x)
    return [q.get(timeout=5) for i in range(len(args))]


urls = ["https://google.com", "https://wikipedia.org"]
responses = schedule(get, *urls)

time.sleep(0.1) # give time for logs to flush

read.Complete(logbox)

import sys
import time
if sys.version_info < (3, 0):
    from Queue import Queue
else:
    from queue import Queue
import threading, requests
from jotting import book, to, read

logbox = "~/Desktop/logbox.txt"
book.distribute(to.File(path=logbox))


def get(queue, url, parent):
    """Get the URL and queue the response."""
    with book("get({url})", parent, url=url):
        try:
            response = requests.get(url)
        except Exception as e:
            queue.put(e)
        else:
            queue.put(response.status_code)


@book.mark
def schedule(function, *args):
    """Create a thread for each mapping of the function to args."""
    q = Queue()
    for x in args:
        # we want to resume the current book
        inputs = (q, x, book.current("tag"))
        threading.Thread(target=function, args=inputs).start()
        book.write(scheduled=x)
    return [q.get(timeout=5) for i in range(len(args))]


urls = ["https://google.com", "https://wikipedia.org"]
responses = schedule(get, *urls)

time.sleep(0.1) # give time for logs to flush

read.Complete(logbox)

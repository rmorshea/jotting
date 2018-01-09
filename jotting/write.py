from queue import Queue
from threading import Thread
from .shelf import book


class Writer(Thread):

    def __init__(self, function=None):
        super().__init__()
        self._inbox = Queue()
        self.daemon = True
        self.start()
        if function is not None:
            self.write = function

    def __call__(self, message):
        self._inbox.put(message)

    def run(self):
        while True:
            message = self._inbox.get()
            try:
                self.write(message)
            except:
                raise
            finally:
                self._inbox.task_done()

    def write(self, message):
        raise NotImlementedError()


class ToFile(Writer):

    def __init__(self, filepath):
        super().__init__()
        self.filepath = filepath

    def write(self, message):
        with open(self.filepath, "a+") as f:
            f.write(message)

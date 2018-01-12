import os
import json
from time import time as now


class WriterMixin(object):

    def __init__(self, target, inbox, stop):
        super(WriterMixin, self).__init__()
        for attr in ("join", "get", "put", "task_done"):
            if not hasattr(inbox, attr):
                raise TypeError("Expected some type of joinable"
                    " queue that implements %r." % attr)
        self.inbox = inbox
        self.daemon = True
        self._target = target
        self._stop = stop
        self.start()

    def __call__(self, log):
        self.inbox.put(log)

    def deadline(self, timeout):
        start = now()
        while not self.inbox.empty():
            if now() - start > timeout:
                self.stop()
                break

    def stop(self):
        self._stop.set()

    def run(self):
        while not self._stop.is_set():
            log = self.inbox.get()
            try:
                self.write(log)
            except:
                raise
            finally:
                self.inbox.task_done()

    def write(self, log):
        self._target(log)

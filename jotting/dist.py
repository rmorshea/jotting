import os
import sys
import json
from time import time as now
from multiprocessing import (
    Process, JoinableQueue as ProcessQueue, Event as ProcessEvent)
if sys.version_info > (3, 0):
    from queue import Queue as ThreadQueue
else:
    from Queue import Queue as ThreadQueue
from threading import Thread, Event as ThreadEvent

from .util import Switch


class DistributorMixin(object):

    def __init__(self, inbox, stop):
        super(DistributorMixin, self).__init__()
        for attr in ("join", "get", "put", "task_done"):
            if not hasattr(inbox, attr):
                raise TypeError("Expected some type of joinable"
                    " queue that implements %r." % attr)
        self.inbox = inbox
        self.daemon = True
        self._outlets = ()
        self._stop = stop
        self.start()

    def set_outlets(self, *outlets):
        self._outlets = outlets

    def __call__(self, log):
        self.inbox.put(log)

    def deadline(self, timeout):
        start = now()
        while not self.inbox.empty():
            if not self.is_alive():
                self.start()
            if now() - start > timeout:
                self.stop()
                break

    def stop(self):
        self._stop.set()

    def run(self):
        while not self._stop.is_set():
            log = self.inbox.get()
            try:
                self.send(log)
            except:
                raise
            finally:
                self.inbox.task_done()

    def send(self, log):
        for o in self._outlets:
            o(log)


class DistributorProcess(DistributorMixin, Process):

    def __init__(self):
        super(DistributorProcess, self).__init__(ProcessQueue(), ProcessEvent())


class DistributorThread(DistributorMixin, Thread):

    def __init__(self):
        super(DistributorThread, self).__init__(ThreadQueue(), ThreadEvent())

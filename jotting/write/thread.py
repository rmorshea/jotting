import sys
from .mixin import WriterMixin
if sys.version_info > (3, 0):
    from queue import Queue as ThreadQueue
else:
    from Queue import Queue as ThreadQueue
from threading import Thread, Event as ThreadEvent


class Writer(WriterMixin, Thread):

    def __init__(self, target=None):
        super(Writer, self).__init__(target, ThreadQueue(), ThreadEvent())

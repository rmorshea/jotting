from .mixin import WriterMixin
from queue import Queue as ThreadQueue
from threading import Thread, Event as ThreadEvent


class Writer(WriterMixin, Thread):

    def __init__(self, target=None):
        super().__init__(target, ThreadQueue(), ThreadEvent())

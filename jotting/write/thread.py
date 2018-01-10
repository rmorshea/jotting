from queue import Queue
from threading import Thread
from .mixin import WriterMixin, ToFileMixin


class Writer(WriterMixin, Thread):

    def __init__(self, target=None):
        super().__init__(target, Queue())


class ToFile(ToFileMixin, Writer): pass

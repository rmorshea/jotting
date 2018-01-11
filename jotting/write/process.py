from .mixin import WriterMixin, ToFileMixin
from multiprocessing import Process, JoinableQueue, Event


class Writer(WriterMixin, Process):

    def __init__(self, target=None):
        super().__init__(target, JoinableQueue(), Event())


class ToFile(ToFileMixin, Writer): pass

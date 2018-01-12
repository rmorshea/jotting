from .mixin import WriterMixin
from multiprocessing import (
    Process, JoinableQueue as ProcessQueue, Event as ProcessEvent)


class Writer(WriterMixin, Process):

    def __init__(self, target=None):
        super(Writer, self).__init__(target, ProcessQueue(), ProcessEvent())

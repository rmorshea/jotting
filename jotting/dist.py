import os
from copy import deepcopy
from .style import Raw


class Distribute:

    def __init__(self, *places):
        self._places = places

    def __call__(self, log):
        for p in self._places:
            p(deepcopy(log))


class Place:

    _style = Raw()

    def __new__(cls, handler=None):
        s = super()
        def init(*args, **kwargs):
            self = s.__new__(cls)
            self.__init__(handler, *args, **kwargs)
            return self
        return init

    def __init__(self, handler, *args, **kwargs):
        self._handler = handler
        self._args = args
        self._kwargs = kwargs
        style = kwargs.pop("style", None)
        if style is not None:
            self._style = style

    def style(self, style, *args, **kwargs):
        self._style = style(*args, **kwargs)

    def __call__(self, log):
        if self._style is not None:
            log = self._style(log)
        if log is not None:
            self._handler(log, *self._args, **self._kwargs)


@Place
def ToFile(log, filepath):
    filepath = os.path.realpath(os.path.expanduser(filepath))
    with open(filepath, "a+") as f:
        f.write(log)

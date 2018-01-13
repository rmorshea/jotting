import os
import sys
from copy import deepcopy
from .style import Raw


def outlet(handler):
    method = staticmethod(handler)
    return type(handler.__name__, (Outlet,), {"_handler": method})


class Outlet(object):

    def __init__(self, style=Raw(), *args, **kwargs):
        self._style = style
        self._args = args
        self._kwargs = kwargs

    def __call__(self, log):
        if self._style is not None:
            log = self._style(log)
        if log is not None:
            self._handler(log, *self._args, **self._kwargs)

    def _handler(self, *args, **kwargs):
        raise NotImplementedError()


@outlet
def File(log, filepath):
    filepath = os.path.realpath(os.path.expanduser(filepath))
    with open(filepath, "a+") as f:
        f.write(log)


@outlet
def Print(log):
    sys.stdout.write(log)

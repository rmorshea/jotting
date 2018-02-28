import os
import sys
from copy import deepcopy
from .style import Raw


def outlet(handler):
    method = staticmethod(handler)
    cls = type(handler.__name__, (Outlet,), {"_handler": method})
    setattr(cls, "__doc__", getattr(handler, "__doc__", None))
    return cls


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
def File(log, path):
    """Send logs to a file.

    Parameters
    ----------
    path : string
        The place you'd like your logs to reside.
    """
    path = os.path.realpath(os.path.expanduser(path))
    with open(path, "a+") as f:
        f.write(log)


@outlet
def Print(log):
    """Send logs to ``sys.stdout``"""
    sys.stdout.write(log)
    sys.stdout.flush()

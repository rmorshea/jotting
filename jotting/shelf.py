import sys
import os
import json
import time
import types
import psutil
import inspect
import asyncio
import threading
import functools
from uuid import uuid1
from weakref import WeakKeyDictionary

from .util import CallMap, infer_title
from .dist import DistributorThread
from . import to, style

if sys.version_info >= (3, 5):
    from ._shelf_py35 import _book_compat
else:
    from ._shelf_py27 import _book_compat


class book(dict, _book_compat):

    _shelves = WeakKeyDictionary()
    _distributor = DistributorThread()
    _distributor.set_outlets(to.Print(style.Tree()))

    @classmethod
    def distribute(cls, *outlets):
        cls._distributor.set_outlets(*outlets)

    def __init__(self, title, parent=None, **content):
        if isinstance(title, str):
            title = title.format(**content)
        parent = parent or self.current().get("tag")
        depth = int(parent.split("-")[1]) + 1 if parent else 0
        super().__init__(tag=uuid1().hex + "-%s" % depth, depth=depth,
            start=time.time(), status="started", parent=parent, title=title)
        self._write(content)
        self._conclusion = {}

    def __enter__(self):
        self.shelf().append(self)
        self.update(status="working")
        return self

    def __exit__(self, *exc):
        self["stop"] = time.time()
        if exc[0] is not None:
            etype = exc[0].__name__
            self.update(status="failure")
            self._conclusion[etype] = str(exc[1])
        else:
            self.update(status="success")
        self._write(self._conclusion)
        self.shelf().pop()
        return False

    def resume(self, tag):
        return self.bind(parent=tag)

    @classmethod
    def write(cls, *args, **kwargs):
        content = dict(*args, **kwargs)
        cls.current()._write(content)

    @classmethod
    def close(cls, *args, **kwargs):
        content = dict(*args, **kwargs)
        cls.current()._conclusion.update(content)

    def _write(self, content):
        process = psutil.Process(os.getpid())
        log = {
            "metadata": self.copy(),
            "content": content,
            "timestamp": time.time(),
            "mem": process.memory_percent(),
            "cpu": process.cpu_percent(),
        }
        self._distributor(log)

    @classmethod
    def current(cls):
        return cls.shelf()[-1]

import sys
import os
import json
import time
import types
import inspect
import threading
import functools
from uuid import uuid1
from weakref import WeakKeyDictionary

from .util import to_title
from .dist import DistributorThread
from . import to, style, read

if sys.version_info >= (3, 5):
    from ._book_py35 import _book_compat
else:
    from ._book_py27 import _book_compat


class book(_book_compat):

    _shelves = WeakKeyDictionary()
    _distributor = DistributorThread()
    _distributor.set_outlets(
        read.Stream(to.Print(style.Tree())))

    @classmethod
    def distribute(cls, *outlets):
        cls._distributor.set_outlets(*outlets)

    def __init__(self, title, parent=None, **content):
        title = to_title(title, content)
        parent = parent or self.current().get("tag")
        self._metadata = dict(title=title, tag=uuid1().hex,
            parent=parent or self.current().get("tag"))
        self._opening = content
        self._conclusion = {}

    def __enter__(self):
        self.shelf().append(self)
        self._metadata.update(
            start=time.time(),
            status="started"
        )
        self._write(self._opening)
        self._metadata["status"] = "working"
        return self

    def __exit__(self, *exc):
        self._metadata["stop"] = time.time()
        if exc[0] is not None:
            etype = exc[0].__name__
            self._metadata.update(status="failure")
            self._conclusion[etype] = str(exc[1])
        else:
            self._metadata.update(status="success")
        self._write(self._conclusion)
        self.shelf().pop()
        return False

    def __len__(self):
        return len(self._metadata)

    def __iter__(self):
        return iter(self._metadata)

    def __getitem__(self, key):
        return self._metadata[key]

    def __repr__(self):
        name = type(self).__name__
        data = map(lambda i: "%s=%s" % i, self._metadata.items())
        return "%s(%s)" % (name, ", ".join(data))

    @property
    def tag(self):
        return self._metadata['tag']

    @property
    def metadata(self):
        return self._metadata.copy()

    def get(self, key, default=None):
        return self._metadata.get(key, default)

    @classmethod
    def write(cls, *args, **kwargs):
        content = dict(*args, **kwargs)
        cls.current()._write(content)

    @classmethod
    def close(cls, *args, **kwargs):
        content = dict(*args, **kwargs)
        cls.current()._conclusion.update(content)

    def _write(self, content):
        log = {
            "metadata": self.metadata,
            "content": content,
            "timestamp": time.time(),
        }
        self._distributor(log)

    @classmethod
    def current(cls):
        return cls.shelf()[-1]

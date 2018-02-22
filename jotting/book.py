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
from . import to, style

if sys.version_info >= (3, 5):
    from ._book_py35 import _book_compat
else:
    from ._book_py27 import _book_compat


class book(_book_compat):

    _shelves = WeakKeyDictionary()
    _distributor = DistributorThread()
    _distributor.set_outlets(to.Print(style.Tree()))

    @classmethod
    def distribute(cls, *outlets):
        cls._distributor.set_outlets(*outlets)

    def __init__(self, title, parent=None, **content):
        title = to_title(title, content)
        parent = parent or self.current().get("tag")
        if parent and parent.startswith("BOOK-"):
            depth = int(parent.rsplit("-", 1)[1]) + 1
        else:
            # this is an arbitrary string or None
            depth = 0
        self._metadata = dict(title=title,
            tag="BOOK-%s-%s" % (uuid1().hex, depth),
            depth=depth, start=time.time(),
            status="started", parent=parent)
        self._write(content)
        self._conclusion = {}

    def __enter__(self):
        self.shelf().append(self)
        self._metadata.update(status="working")
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

    @property
    def tag(self):
        return self._metadata['tag']

    @property
    def metadata(self):
        return self._metadata.copy()

    def __len__(self):
        return len(self._metadata)

    def __iter__(self):
        return iter(self._metadata)

    def __getitem__(self, key):
        return self._metadata[key]

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

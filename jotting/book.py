import sys
import os
import json
import time
import types
import inspect
import threading
import functools
from uuid import uuid4
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
    _distributor_type = DistributorThread
    _distributor_inst = DistributorThread()

    def __init__(self, title, parent=None, **content):
        title = to_title(title, content)
        parent = parent or self.current("tag")
        self._opening = content
        self._conclusion = {}
        self._metadata = {
            "title": title,
            "timestamps": (),
            "tag": uuid4().hex,
            "parent": parent,
        }

    @classmethod
    def distribute(cls, *outlets):
        cls._distributor_inst.set_outlets(*outlets)

    @property
    def tag(self):
        return self._metadata['tag']

    @property
    def status(self):
        return self._metadata["status"]

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

    @classmethod
    def current(cls, data=None):
        now = cls.shelf()[-1]
        if data is None:
            return now
        elif now is not None:
            return now._metadata.get(data)

    @classmethod
    def outlets(cls):
        return cls._distributor_inst._outlets

    def _write(self, content):
        self._metadata["timestamps"] += (time.time(),)
        self._distributor({"metadata": self.metadata, "content": content})

    @property
    def _distributor(self):
        if not self._distributor_inst.is_alive():
            # restart the distributor daemon
            new = self._distributor_type()
            new.set_outlets(*self.outlets())
            type(self)._distributor_inst = new
        return self._distributor_inst

    def __enter__(self):
        self.shelf().append(self)
        self._metadata["status"] = "started"
        self._write(self._opening)
        self._metadata["status"] = "working"
        return self

    def __exit__(self, *exc):
        self._metadata["stop"] = time.time()
        if exc[0] is not None:
            etype = exc[0].__name__
            self._metadata["status"] = "failure"
            self._conclusion[etype] = str(exc[1])
        else:
            self._metadata["status"] = "success"
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

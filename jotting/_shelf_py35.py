import os
import sys
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

from .utils import CallMap, infer_title
from .style import Tree


class book(dict):

    _shelves = WeakKeyDictionary()

    @classmethod
    def edit(cls, **options):
        for k, v in options.items():
            if k.strip("_") != k:
                raise TypeError("%r is an invalid option name." % k[1:-1])
            k = "_" + k + "_"
            if not hasattr(cls, k):
                raise TypeError("%r is not an editable option." % k[1:-1])
            setattr(cls, k, v)

    def __init__(self, title=None, parent=None, **content):
        parent = parent or self.current().get("tag")
        depth = int(parent.split("-")[1]) + 1 if parent else 0
        title = title or "%s - task" % self.current().get("title")
        super().__init__(
            tag=uuid1().hex + "-%s" % depth,
            depth=depth, start=time.time(),
            status="started", parent=parent, title=title)
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
            self._conclusion.setdefault("reason", etype)
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
        content.setdefault("reason", None)
        self._writer_({
            "metadata": self.copy(),
            "content": content,
            "timestamp": time.time(),
            "mem": process.memory_percent(),
            "cpu": process.cpu_percent()})

    def _writer_(self, log, style=Tree()):
        sys.stdout.write(style(log))

    @classmethod
    def current(cls):
        return cls.shelf()[-1]

    @classmethod
    def shelf(cls):
        task = asyncio.Task.current_task() or threading.current_thread()
        if task not in cls._shelves:
            cls._shelves[task] = [{"title": "__main__"}]
        return cls._shelves[task]

    @classmethod
    def mark(cls, title, *binding, **content):
        def setup(function, title=title):
            if title is None:
                title = infer_title(function)
            cm = CallMap(function)
            if inspect.iscoroutinefunction(function):
                @functools.wraps(function)
                async def author(*args, **kwargs):
                    book = kwargs.pop("__book__", None)
                    intro = dict(content, **cm.map(args, kwargs))
                    with book or cls(title, *binding, **intro):
                        result = await function(*args, **kwargs)
                        cls.close({"returned": result})
                        return result
            else:
                @functools.wraps(function)
                def author(*args, **kwargs):
                    book = kwargs.pop("__book__", None)
                    intro = dict(content, **cm.map(args, kwargs))
                    with book or cls(title, *binding, **intro):
                        result = function(*args, **kwargs)
                        cls.close({"returned": result})
                        return result
            return author
        if callable(title):
            return setup(title, None)
        else:
            return setup

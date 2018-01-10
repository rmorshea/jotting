import sys
import json
import time
import types
import inspect
import asyncio
import threading
import functools
from uuid import uuid1
from weakref import WeakKeyDictionary

from .utils import CallMap, infer_title
from .style import Log


class book(dict):

    _allow_ = False
    _writer_ = Log()
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
            status="started", parent=parent, title=title,
            tag=uuid1().hex + "-%s" % depth, depth=depth)
        self._publisher_(content)
        self._conclusion = None

    def __enter__(self):
        self.shelf().append(self)
        self.update(status="working")
        return self

    def __exit__(self, *exc):
        trial = Exception if self._allow_ is True else self._allow_
        not_raises = issubclass(exc[0], trial) if self._allow_ else trial
        if exc[0] is not None:
            self.update(status="failure")
            self._publisher_({exc[0].__name__: str(exc[1])})
        elif self._conclusion is not None:
            self.update(status="success")
            self._publisher_(self._conclusion)
        else:
            self.update(status="success")
            self._publisher_({})
        self.shelf().pop()
        return not_raises

    def resume(self, tag):
        return self.bind(parent=tag)

    @classmethod
    def write(cls, *args, **kwargs):
        content = dict(*args, **kwargs)
        cls.current()._publisher_(content)

    @classmethod
    def close(cls, *args, **kwargs):
        content = dict(*args, **kwargs)
        cls.current()._conclusion = content

    def _publisher_(self, content):
        metadata = self.copy()
        metadata["timestamp"] = time.time()
        self._writer_({"metadata": metadata, "content": content})

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

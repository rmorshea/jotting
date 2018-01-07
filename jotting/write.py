import sys
import json
import time
import inspect
import asyncio
import threading
import functools
from uuid import uuid1
from weakref import WeakKeyDictionary

from .utils import CallMap, infer_title


class book:

    _try_ = False
    _file_ = sys.stdout
    _shelves = WeakKeyDictionary()

    @classmethod
    def edit(cls, **options):
        for k, v in options.items():
            k = "_" + k + "_"
            if not hasattr(cls, k):
                raise TypeError("%r is not an editable option." % k[1:-1])
            setattr(cls, k, v)

    def __init__(self, title, *binding, **content):
        self._binding = dict(binding,
            title=title.format(**content),
            tag=str(uuid1()), status="started")
        self._binding.setdefault("parent", self.current())
        for k in list(self._binding):
            if k.startswith("_"):
                v = self._binding.pop(k)
                k += "_"
                if not hasattr(self, k):
                    raise TypeError("%r is not an editable option." % k[1:-1])
                setattr(self, k, v)
        self._publisher_(content)
        self._conclusion = None

    def __enter__(self):
        self._shelf().append(self)
        self.update(status="working")
        return self

    def __exit__(self, *exc):
        trial = Exception if self._try_ is True else self._try_
        not_raises = issubclass(exc[0], trial) if self._try_ else trial
        if exc[0] is not None:
            self.update(status="failure")
            self._publisher_({exc[0].__name__: str(exc[1])})
        elif self._conclusion is not None:
            self.update(status="success")
            self._publisher_(self._conclusion)
        else:
            self.update(status="success")
            self._publisher_({})
        self._shelf().pop()
        return not_raises

    @classmethod
    def write(cls, *args, **kwargs):
        content = dict(*args, **kwargs)
        cls._current()._publisher_(content)

    @classmethod
    def close(cls, *args, **kwargs):
        content = dict(*args, **kwargs)
        cls._current()._conclusion = content

    def get(self, key):
        return self._binding.get(key)

    def update(self, *args, **kwargs):
        self._binding.update(*args, **kwargs)

    def _publisher_(self, content):
        metadata = self._binding.copy()
        metadata["timestamp"] = time.time()
        self._writer_({"metadata": metadata, "content": content})

    def _writer_(self, content):
        message = self._serializer_(content)
        self._file_.write(message + "\n")

    def _serializer_(self, message):
        try:
            return json.dumps(message)
        except:
            return str(message)

    @classmethod
    def current(self):
        return self.shelf(-1)

    @classmethod
    def shelf(cls, index=None):
        if index is not None:
            return cls._shelf()[-1].get("tag")
        else:
            return [s.get("tag") for s in cls._shelf()]

    @classmethod
    def _current(cls):
        return cls._shelf()[-1]

    @classmethod
    def _shelf(cls):
        task = asyncio.Task.current_task() or threading.current_thread()
        if task not in cls._shelves:
            cls._shelves[task] = [{}]
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

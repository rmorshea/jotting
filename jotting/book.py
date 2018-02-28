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
        """Create a new book for logging.

        Parameters
        ----------
        title : string, function, or class
            A string representing the title of the book. For functions and
            classes, a title is infered from its title, and module. Inference
            attempt to drill down into closures to determin the root function,
            or class. This typically happens when a function or class has many
            decorators.
        parent : string or None
            The tag of the last book. If ``None`` then the last book within the
            current thread is used. To link across threads or processes, you must
            manually communicate this.
        **content : any
            A dictionary of content that will be logged when the book is opened.
        """
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
        """Set which :class:`jotting.to.Outlet` objects recieve logs."""
        cls._distributor_inst.set_outlets(*outlets)

    @property
    def tag(self):
        """Get this book's tag."""
        return self._metadata['tag']

    @property
    def status(self):
        """Get this book's tag.

        Returns
        -------
        'started', 'working', 'success', or 'failure'.
        """
        return self._metadata["status"]

    @property
    def metadata(self):
        """Get a copy of this book's metadata."""
        return self._metadata.copy()

    @classmethod
    def write(cls, *args, **kwargs):
        """Write a log to the currently open book."""
        content = dict(*args, **kwargs)
        cls.current()._write(content)

    @classmethod
    def conclude(cls, *args, **kwargs):
        """Write the content that will be logged when the book closes."""
        content = dict(*args, **kwargs)
        cls.current()._conclusion.update(content)

    @classmethod
    def current(cls, data=None):
        """Get the current book, or metadata from the current book.

        Parameters
        ----------
        data : string or None
            A string indicating a desired piece of metadata from the current
            book. If ``None``, then the current book is returned instead.

        Returns
        -------
        The current book, or an entry in its metadata.
        """
        now = cls.shelf()[-1]
        if data is None:
            return now
        elif now is not None:
            return now._metadata.get(data)

    @classmethod
    def outlets(cls):
        """Get the outlets for all books."""
        return cls._distributor_inst._outlets

    def _write(self, content):
        """Send a message with the given content to the distributor."""
        self._metadata["timestamps"] += (time.time(),)
        msg = {"metadata": self._metadata.copy(), "content": content}
        self._distribute(msg)

    @classmethod
    def _distribute(cls, msg):
        """Pushes a message to the distributor.

        If the distributor has died, a new one is created in its place. This
        usually happens when a new process is started, and the old reference
        is marked as dead.

        Parameters
        ----------
        msg : dictionary
            An pickleable dictionary containing data that the distributor's
            outlets know how to handle and format.
        """
        if not cls._distributor_inst.is_alive():
            # restart the distributor daemon
            new = cls._distributor_type()
            new.set_outlets(*cls.outlets())
            type(cls)._distributor_inst = new
        return cls._distributor_inst.send(msg)

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

import inspect
import asyncio
import functools
import threading

from .util import CallMap


class _book_compat(object):

    @classmethod
    def shelf(cls):
        """A list of all open :class:`jotting.book`s in the current context.

        Returns
        -------
        A list of :class:`jotting.book` objects.
        """
        try:
            task = asyncio.Task.current_task()
        except RuntimeError:
            task = None
        task = task or threading.current_thread()
        if task not in cls._shelves:
            cls._shelves[task] = [None]
        return cls._shelves[task]

    @classmethod
    def mark(cls, title=None, *binding, **content):
        """Decorate a function to record when it start, succeeds, or fails.

        The function is called within the context of a :class:`jotting.book`.

        Parameters
        ----------
        title : string or None
            The title of the book for this function. If no title is given, then
            it's infered based on the name, and module of what's been decorated.
        *binding : any
            Arguments passed directly to :class:`jotting.book`.
        **contents : any
            Keywords passed directly to :class:`jotting.book`.
        """
        def setup(function):
            cm = CallMap(function)
            if inspect.iscoroutinefunction(function):
                @functools.wraps(function)
                async def author(*args, **kwargs):
                    book = kwargs.pop("__book__", None)
                    intro = dict(content, **cm.map(args, kwargs))
                    with book or cls(title or function, *args, **intro):
                        result = await function(*args, **kwargs)
                        cls.conclude({"returned": result})
                        return result
            elif inspect.isgeneratorfunction(function):
                @functools.wraps(function)
                def author(*args, **kwargs):
                    book = kwargs.pop("__book__", None)
                    intro = dict(content, **cm.map(args, kwargs))
                    with book or cls(title or function, *args, **intro):
                        result = function(*args, **kwargs)
                        cls.conclude({"returned": result})
                        yield from result
            else:
                @functools.wraps(function)
                def author(*args, **kwargs):
                    book = kwargs.pop("__book__", None)
                    intro = dict(content, **cm.map(args, kwargs))
                    with book or cls(title or function, *args, **intro):
                        result = function(*args, **kwargs)
                        cls.conclude({"returned": result})
                        return result
            return author
        if callable(title):
            return setup(title)
        else:
            return setup

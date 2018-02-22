import inspect
import functools

from .util import CallMap


class _book_compat(object):

    @classmethod
    def shelf(cls):
        task = threading.current_thread()
        if task not in cls._shelves:
            cls._shelves[task] = [{"title": "__main__"}]
        return cls._shelves[task]

    @classmethod
    def mark(cls, title=None, *binding, **content):
        def setup(function):
            cm = CallMap(function)
            @functools.wraps(function)
            def author(*args, **kwargs):
                book = kwargs.pop("__book__", None)
                intro = dict(content, **cm.map(args, kwargs))
                with book or cls(title or function, *binding, **intro):
                    result = function(*args, **kwargs)
                    cls.close({"returned": result})
                    return result
            return author
        if callable(title):
            return setup(title)
        else:
            return setup

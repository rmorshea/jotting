import asyncio
from uuid import uuid1
from collections import defaultdict
from weakref import WeakKeyDictionary

from .. import utils
from .paper import paper


class book:

    ptype = paper
    class _main: pass
    _stacks = WeakKeyDictionary()
    _namespaces = defaultdict(lambda: dict(tag=None, _children=[], parent=None))

    def __init__(self, *args, **kwargs):
        self.data = utils.merge({}, *args, **kwargs)

    @property
    def stack(self):
        task = asyncio.Task.current_task() or self._main
        return self._stacks.setdefault(task, [])

    def namespace(self, n):
        try:
            tag = self.stack[-(1 + n)]
        except IndexError:
            tag = None
        return self._namespaces[tag]

    @property
    def main(self):
        stack = self._stacks.setdefault(self._main, [])
        if not stack:
            return {}
        else:
            return self._namespaces[stack[-1]]

    @property
    def last(self):
        return self.namespace(1)

    @property
    def current(self):
        return self.namespace(0)

    def __enter__(self):
        tag = str(uuid1())
        self.stack.append(tag)
        new = self.current
        new["tag"] = tag
        last = self.last
        last["_children"].append(tag)
        new["parent"] = last["tag"]
        utils.merge(new, last, self.main, **self.data)
        return self.ptype(new)

    def __exit__(self, *exc):
        del self._namespaces[self.stack.pop()]

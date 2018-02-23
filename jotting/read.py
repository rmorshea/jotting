import os
import json
from .to import Print
from .style import Tree
from .util import Switch
from collections import defaultdict


class Stream(Switch):

    def __init__(self, outlet=Print(Tree())):
        self._logs = {} # series of log queues per tag
        self._tree = {} # the tag paths to each log
        self._sending = None
        self._pending = []
        self._outlet = outlet

    def __call__(self, log):
        if isinstance(log, str):
            log = json.loads(log)
        self._switch(log)

    def _started(self, log):
        metadata = log["metadata"]
        tag = metadata["tag"]
        parent = metadata["parent"]
        self._logs[tag] = [log]
        lineage = self._tree.setdefault(parent, [])
        self._tree[tag] = lineage + [tag]

    def _working(self, log):
        tag = log["metadata"]["tag"]
        self._logs[tag].append(log)

    def _default(self, log):
        tag = log["metadata"]["tag"]
        if self._sending is None:
            self._send(log)
        elif self._sending == self._tree.get(tag, [None])[0]:
            self._send(log)
        else:
            self._pending.append(log)

    def _send(self, log):
        tag = log["metadata"]["tag"]
        for t in self._tree[tag]:
            queue = self._logs[t]
            for _ in range(len(queue)):
                self._push(queue.pop(0))
        self._push(log)
        if log["metadata"]["parent"] is None:
            self._sending = None
            if self._pending:
                self._send(self._pending.pop(0))
        else:
            self._sending = self._tree[tag][0]
        del self._logs[tag]
        del self._tree[tag]

    def _push(self, log):
        tag = log["metadata"]["tag"]
        depth = len(self._tree[tag]) - 1
        log["metadata"]["depth"] = depth
        self._outlet(log)


class File(Switch):

    def __init__(self, filename):
        filename = os.path.realpath(os.path.expanduser(filename))
        with open(filename, "r") as f:
            lines = f.read().split("\n")
            logs = map(json.loads, (l for l in lines if l))
        todo = sorted(logs, key=lambda l: l["timestamp"])

        started = [None]
        self._order = []
        while len(todo):
            self._switch(todo.pop(0), started, self._order, todo)

    def _started(self, log, started, order, todo):
        tag = log["metadata"]["tag"]
        parent = log["metadata"]["parent"]
        if started[-1] != parent:
            todo.append(log)
        else:
            started.append(tag)
            order.append(log)

    def _working(self, log, started, order, todo):
        parent = log["metadata"]["parent"]
        if started[-1] != parent:
            todo.append(log)
        else:
            order.append(log)

    def _default(self, log, started, order, todo):
        tag = log["metadata"]["tag"]
        ahead = map(lambda l : l["metadata"]["parent"], todo)
        if started[-1] == tag and tag not in ahead:
            started.pop()
            order.append(log)
        else:
            todo.append(log)

    def __call__(self, outlet=Stream(Print(Tree()))):
        list(map(outlet, self._order))

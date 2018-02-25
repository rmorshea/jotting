import os
import json
from .style import Tree
from .util import Switch


class Complete(object):

    def __init__(self, source):
        if isinstance(source, str):
            path = os.path.realpath(os.path.expanduser(source))
            with open(path, "r") as f:
                lines = f.read().split("\n")
                source = map(json.loads, (l for l in lines if l))
        self._logs = self._load(source)

    def _load(self, source):
        logs, working, done = [], [], []
        start = lambda l: l["metadata"]["timestamps"][0]
        for l in sorted(source, key=start):
            status = l["metadata"]["status"]
            if status == "started":
                logs.append(l)
            elif status == "working":
                working.append(l)
            else:
                done.append(l)
        self._insert(logs, working)
        self._insert(logs, done)
        return logs

    def _insert(self, logs, todo):
        index = len(logs) - 1
        while len(todo):
            t = todo.pop()
            t_m = t["metadata"]
            t_t = t_m["timestamps"][-1]
            for i, l in enumerate(reversed(logs)):
                l_m = l["metadata"]
                l_t = l_m["timestamps"][-1]
                if t_m["tag"] in (l_m["tag"], l_m["parent"]) and l_t < t_t:
                    logs.insert(len(logs) - i, t)
                    break
            else:
                raise ValueError("Incomplete log set.")

    def __iter__(self):
        return iter(self._logs)

    def __repr__(self):
        return "".join(map(Tree(), self._logs))


class Stream(Switch):

    def __init__(self, *outlets):
        self._hold = [] # all the logs up to that point
        self._outlets = outlets

    def __call__(self, log):
        if isinstance(log, str):
            log = json.loads(log)
        self._switch(log)

    def _started(self, log):
        tag = log["metadata"]["tag"]
        parent = log["metadata"]["parent"]
        self._hold.append(log)

    def _working(self, log):
        self._hold.append(log)

    def _default(self, log):
        for i, l in enumerate(reversed(self._hold)):
            meta = l["metadata"]
            if log["metadata"]["tag"] in (meta["parent"], meta["tag"]):
                self._hold.insert(-i, log)
                break
        else:
            self._hold.append(log)
        done = set()
        send = []
        for i, l in enumerate(reversed(self._hold)):
            m = l["metadata"]
            if m["status"] in ("success", "failure"):
                done.add(m["tag"])
            if m["status"] == "started":
                if m["tag"] not in done:
                    send.insert(0, l)
                else:
                    send.append(l)
            else:
                send.append(l)
        list(map(self._send, send))
        self._hold.clear()

    def _send(self, log):
        for o in self._outlets:
            o(log)

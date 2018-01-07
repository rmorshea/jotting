import sys
import json
import datetime


class Tree(object):

    def __init__(self, write=sys.stdout.write):
        self._write = write

    def __call__(self, content, metadata, depth):
        method = getattr(self, metadata['status'])
        lines = list(method(content, metadata, depth))
        self._write("\n" + "\n".join(lines))

    def started(self, content, metadata, depth):
        indent = "|   " * depth
        yield indent + "|-- {status}: {title}".format(**metadata)
        yield indent + "|   @ {0}".format(datetime.datetime.fromtimestamp(metadata["timestamp"]))
        for k, v in content.items():
            yield indent + "|   | {0}: {1}".format(k, v)

    def working(self, content, metadata, depth):
        indent = "|   " * (depth + 1)
        yield indent + "|-- {status}: {title}".format(**metadata)
        yield indent + "|   @ {0}".format(datetime.datetime.fromtimestamp(metadata["timestamp"]))
        for k, v in content.items():
            yield indent + "|   | {0}: {1}".format(k, v)

    def success(self, content, metadata, depth):
        indent = "|   " * (depth + 1)
        yield indent + "`-- {status}: {title}".format(**metadata)
        yield indent + "    @ {0}".format(datetime.datetime.fromtimestamp(metadata["timestamp"]))
        for k, v in content.items():
            yield indent + "    | {0}: {1}".format(k, v)

    def failure(self, content, metadata, depth):
        indent = "|   " * (depth + 1)
        yield indent + "`-- {status}: {title}".format(**metadata)
        yield indent + "    @ {0}".format(datetime.datetime.fromtimestamp(metadata["timestamp"]))
        for k, v in content.items():
            yield indent + "    | {0}: {1}".format(k, v)


class Stream:

    def __init__(self, outlet=Tree()):
        self._logs = {} # series of log queues per tag
        self._tree = {None: []} # the tag paths to each log
        self._sending = None
        self._pending = []
        self._outlet = outlet

    def __call__(self, log):
        if isinstance(log, str):
            log = json.loads(log)
        status = log["metadata"].get("status")
        if status == "started":
            self._start(log)
        elif status == "working":
            self._continue(log)
        elif status in ("success", "failure"):
            self._close(log)
        else:
            raise ValueError("Invalid status %r" % status)

    def _start(self, log):
        metadata = log["metadata"]
        tag = metadata["tag"]
        parent = metadata["parent"]
        self._logs[tag] = [log]
        self._tree[tag] = self._tree[parent] + [tag]

    def _continue(self, log):
        tag = log["metadata"]["tag"]
        self._logs[tag].append(log)

    def _close(self, log):
        tag = log["metadata"]["tag"]
        if self._sending is None:
            self._send(log)
        elif self._sending == self._tree[tag][0]:
            self._send(log)
        else:
            self._pending.append(log)

    def _send(self, log):
        tag = log["metadata"]["tag"]
        for i, t in enumerate(self._tree[tag]):
            queue = self._logs[t]
            for _ in range(len(queue)):
                self._pre_outlet(queue.pop(0), i)
        self._pre_outlet(log, i)
        if log["metadata"]["parent"] is None:
            self._sending = None
            if self._pending:
                self._send(self._pending.pop(0))
        else:
            self._sending = self._tree[tag][0]
        del self._logs[tag]
        del self._tree[tag]

    def _pre_outlet(self, log, depth):
        self._outlet(log["content"], log["metadata"], depth)

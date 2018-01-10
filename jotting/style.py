import sys
import json
import datetime


class Style:

    def __init__(self, writer=sys.stdout.write):
        self._writer = writer

    def __call__(self, log):
        content, metadata = log["content"], log["metadata"]
        method = getattr(self, metadata['status'], self.default)
        lines = method(content, metadata, metadata["depth"])
        lines = [lines] if isinstance(lines, str) else lines
        self._writer("\n".join(lines) + "\n")

    def default(self, content, metadata, depth):
        raise NotImlementedError()


class Log(Style):

    def default(self, content, metadata, depth):
        timestamp = datetime.datetime.fromtimestamp(metadata["timestamp"])
        status, title = metadata["status"], metadata["title"]
        content = ", ".join("%s: %s" % (k, v) for k, v in content.items())
        yield "{0} [{1}] {2} - {3}".format(timestamp, status, title, content)


class Tree(Style):

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

    def __init__(self, outlet=Log()):
        self._logs = {} # series of log queues per tag
        self._tree = {} # the tag paths to each log
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
        tree = self._tree.setdefault(parent, [])
        self._tree[tag] = tree + [tag]

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
        for t in self._tree[tag]:
            queue = self._logs[t]
            for _ in range(len(queue)):
                self._outlet(queue.pop(0))
        self._outlet(log)
        if log["metadata"]["parent"] is None:
            self._sending = None
            if self._pending:
                self._send(self._pending.pop(0))
        else:
            self._sending = self._tree[tag][0]
        del self._logs[tag]
        del self._tree[tag]

import sys
import json
import types
import inspect
import datetime


class stream:

    def __new__(cls, outlet):
        new = super().__new__
        def __init__(*args, **kwargs):
            self = new(cls)
            self.__init__(outlet, *args, **kwargs)
            return self
        return __init__

    def __init__(self, outlet, *args, **kwargs):
        self._logs = {} # series of log queues per tag
        self._tree = {None: []} # the tag paths to each log
        self._sending = None
        self._pending = []
        if not callable(outlet) or inspect.isclass(outlet):
            if inspect.isclass(outlet):
                outlet = outlet(*args, **kwargs)
            def outlet(content, metadata, depth, _outlet=outlet):
                status = metadata["status"]
                if hasattr(_outlet, status):
                    handler = getattr(_outlet, status)
                    handler(content, metadata, depth)
        self._outlet = outlet

    def __call__(self, log):
        if isinstance(log, str):
            log = json.loads(log)
        status = log["metadata"].get("status")
        if status == "started":
            self._start(log)
        elif status == "running":
            self._continue(log)
        else:
            self._close(log)

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

def info(data):
    lines = []
    for name, entry in data.item():
        if isinstance(entry, dict):
            lines.append("├ %s:" % name)
            lines.extend("|   • %s = %s" % i for i in entry.items())
        elif isinstnace(entry, list):
            lines.append("├ %s:" % name)
            lines.extend("|   • %s" % i for i in entry.items())
        else:
            lines.append("%s: %s" % (name, entry))
    return lines


@stream
class tree:

    def __init__(self, file=sys.stdout, entry_length=75):
        self._entry_length = entry_length
        self._file = file

    def _write(self, text):
        self._file.write(text)

    def _insert_indent(self, lines, indent):
        for i in range(len(lines)):
            lines.insert(2 * i, "\n" + indent)

    def started(self, arguments, metadata, depth):
        indent = "|   " * depth
        lines = ["|-- {status}: {action}".format(**metadata),
            "|   @ {0}".format(datetime.datetime.fromtimestamp(metadata["timestamp"]))]
        for k, v in arguments.items():
            lines.append("|   | {0}: {1}".format(k, v))
        self._insert_indent(lines, indent)
        self._write("".join(lines))

    def running(self, content, metadata, depth):
        indent = "|   " * (depth + 1)
        lines = ["|-- {status}: {action} ".format(**metadata),
            "|   @ {0}".format(datetime.datetime.fromtimestamp(metadata["timestamp"]))]
        for k, v in content.items():
            lines.append("|   | {0}: {1}".format(k, v))
        self._insert_indent(lines, indent)
        self._write("".join(lines))

    def success(self, content, metadata, depth):
        indent = "|   " * (depth + 1)
        lines = ["`-- {status}: {action} ".format(**metadata),
            "    @ {0}".format(datetime.datetime.fromtimestamp(metadata["timestamp"]))]
        for k, v in content.items():
            lines.append("    | {0}: {1}".format(k, v))
        self._insert_indent(lines, indent)
        self._write("".join(lines))

    def failure(self, content, metadata, depth):
        indent = "|   " * (depth + 1)
        lines = ["`-- {status}: {action} ".format(**metadata),
            "|   @ {0}".format(datetime.datetime.fromtimestamp(metadata["timestamp"]))]
        for k, v in content.items():
            lines.append("    | {0}: {1}".format(k, v))
        self._insert_indent(lines, indent)
        self._write("".join(lines))

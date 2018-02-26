import sys
import json
import datetime
import inspect
from .util import Switch


class Style(Switch):

    def __init__(self):
        self._depths = {}

    def __call__(self, log):
        log = self._pre(log)
        if log:
            lines = self._switch(log)
            if lines and isinstance(lines, str):
                lines = [lines]
            else:
                lines = list(lines)
            if lines:
                return self._post("\n".join(lines) + "\n")

    def _pre(self, log):
        tag = log["metadata"]["tag"]
        parent = log["metadata"]["parent"]
        depth = self._depths.get(parent, -1) + 1
        log["metadata"]["depth"] = self._depths[tag] = depth
        return log

    def _post(self, log):
        return log


class Raw(Style):

    class Encoder(json.JSONEncoder):

        def default(self, o):
            try:
                return super(json.JSONEncoder, self).default(o)
            except:
                return str(o)

    def _default(self, log):
        return self.Encoder().encode(log)


class Log(Style):

    def _pre(self, log):
        if isinstance(log["metadata"]["title"], str):
            return super(Log, self)._pre(log)

    def _completed(self, log):
        metadata = log["metadata"]
        status = metadata["status"]
        duration = metadata["timestamps"][-1] - metadata["timestamps"][0]
        timestamp = datetime.datetime.fromtimestamp(metadata["timestamps"][-1])
        info = ", ".join(map(lambda i: "%s: %s" % i, log["content"].items()))
        message = "{time} {status} {title} after {duration:.3f} seconds"
        if len(info) > 50:
            info = info[:47] + "..."
        if info:
            message += " - {info}"
        yield message.format(time=timestamp, status=status.upper(),
            title=metadata["title"], info=info, duration=duration)

    _success = _completed
    _failure = _completed


class Tree(Style):

    def _started(self, log):
        content, metadata = log["content"], log["metadata"]
        indent = "|   " * metadata["depth"]
        timestamp = datetime.datetime.fromtimestamp(metadata["timestamps"][-1])
        yield indent + "|-- {status}: {title}".format(**metadata)
        yield indent + "|   @ {0}".format(timestamp)
        if "reason" in content:
            yield indent + "|   | reason: {0}".format(content.pop("reason"))
        for k, v in content.items():
            yield indent + "|   | {0}: {1}".format(k, v)

    def _working(self, log):
        content, metadata = log["content"], log["metadata"]
        indent = "|   " * (metadata["depth"] + 1)
        timestamp = datetime.datetime.fromtimestamp(metadata["timestamps"][-1])
        yield indent + "|-- {status}: {title}".format(**metadata)
        yield indent + "|   @ {0}".format(timestamp)
        if "reason" in content:
            yield indent + "|   | reason: {0}".format(content.pop("reason"))
        for k, v in content.items():
            yield indent + "|   | {0}: {1}".format(k, v)

    def _default(self, log):
        content, metadata = log["content"], log["metadata"]
        indent = "|   " * (metadata["depth"] + 1)
        timestamp = datetime.datetime.fromtimestamp(metadata["timestamps"][-1])
        yield indent + "`-- {status}: {title}".format(**metadata)
        yield indent + "    @ {0}".format(timestamp)
        diff = metadata["timestamps"][-1] - metadata["timestamps"][0]
        content["duration"] = "{:.3f}".format(diff) + " seconds"
        if "reason" in content:
            yield indent + "|   | reason: {0}".format(content.pop("reason"))
        for k, v in content.items():
            yield indent + "    | {0}: {1}".format(k, v)

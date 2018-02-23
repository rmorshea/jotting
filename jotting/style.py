import sys
import json
import datetime
import inspect
from .util import Switch


class Style(Switch):

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
            return log

    def _completed(self, log):
        metadata = log["metadata"]
        status = metadata["status"]
        duration = metadata["stop"] - metadata["start"]
        timestamp = datetime.datetime.fromtimestamp(log["timestamp"])
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

    def _pre(self, log):
        if "depth" not in log["metadata"]:
            from .read import Stream
            raise TypeError((
                "A depth was not added to the log's metadata. "
                "Try wrapping this style in a buffer like %r "
                "that will determine a logs depth, and add it to its metadata."
            ) % Stream)
        return log

    def _started(self, log):
        content, metadata = log["content"], log["metadata"]
        indent = "|   " * metadata["depth"]
        timestamp = datetime.datetime.fromtimestamp(log["timestamp"])
        yield indent + "|-- {status}: {title}".format(**metadata)
        yield indent + "|   @ {0}".format(timestamp)
        if "reason" in content:
            yield indent + "|   | reason: {0}".format(content.pop("reason"))
        for k, v in content.items():
            yield indent + "|   | {0}: {1}".format(k, v)

    def _working(self, log):
        content, metadata = log["content"], log["metadata"]
        indent = "|   " * (metadata["depth"] + 1)
        timestamp = datetime.datetime.fromtimestamp(log["timestamp"])
        yield indent + "|-- {status}: {title}".format(**metadata)
        yield indent + "|   @ {0}".format(timestamp)
        if "reason" in content:
            yield indent + "|   | reason: {0}".format(content.pop("reason"))
        for k, v in content.items():
            yield indent + "|   | {0}: {1}".format(k, v)

    def _success(self, log):
        content, metadata = log["content"], log["metadata"]
        indent = "|   " * (metadata["depth"] + 1)
        timestamp = datetime.datetime.fromtimestamp(log["timestamp"])
        yield indent + "`-- {status}: {title}".format(**metadata)
        yield indent + "    @ {0}".format(timestamp)
        diff = metadata["stop"] - metadata["start"]
        content["duration"] = "{:.3f}".format(diff) + " seconds"
        if "reason" in content:
            yield indent + "|   | reason: {0}".format(content.pop("reason"))
        for k, v in content.items():
            yield indent + "    | {0}: {1}".format(k, v)

    def _failure(self, log):
        content, metadata = log["content"], log["metadata"]
        indent = "|   " * (metadata["depth"] + 1)
        timestamp = datetime.datetime.fromtimestamp(log["timestamp"])
        yield indent + "`-- {status}: {title}".format(**metadata)
        yield indent + "    @ {0}".format(timestamp)
        diff = metadata["stop"] - metadata["start"]
        content["duration"] = "{:.3f}".format(diff) + " seconds"
        if "reason" in content:
            yield indent + "|   | reason: {0}".format(content.pop("reason"))
        for k, v in content.items():
            yield indent + "    | {0}: {1}".format(k, v)

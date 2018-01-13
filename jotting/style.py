import sys
import json
import datetime
import inspect

from .utils import infer_title


class Style(object):

    default = None

    def __call__(self, log):
        method = getattr(self, log["metadata"]["status"], self.default)
        if method is not None:
            log = self._pre(log)
            if log:
                lines = method(log)
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

    def default(self, log):
        try:
            return json.dumps(log)
        except:
            content = {k: str(v) for k, v in log["content"].items()}
            return json.dumps(dict(log, content=content))


class Log(Style):

    def _pre(self, log):
        if isinstance(log["metadata"]["title"], str):
            return log

    def started(self, log):
        metadata = log["metadata"]
        status = metadata["status"]
        timestamp = datetime.datetime.fromtimestamp(log["timestamp"])
        info = "mem: %{:.6}, cpu: %{:.6}".format(log["mem"], log["cpu"])
        yield "{time} [{status}] {title} - {info}".format(
            time=timestamp, status=status, title=metadata["title"], info=info)

    def working(self, log):
        metadata = log["metadata"]
        status = metadata["status"]
        timestamp = datetime.datetime.fromtimestamp(log["timestamp"])
        info = "mem: %{:.6}, cpu: %{:.6}".format(log["mem"], log["cpu"])
        yield "{time} [{status}] {title} - {info}".format(
            time=timestamp, status=status, title=metadata["title"], info=info)

    def success(self, log):
        metadata = log["metadata"]
        status = metadata["status"]
        duration = metadata["stop"] - metadata["start"]
        timestamp = datetime.datetime.fromtimestamp(log["timestamp"])
        info = "mem: %{:.6}, cpu: %{:.6}".format(log["mem"], log["cpu"])
        message = "{time} [{status}] {title} after {duration:.3f} seconds - {info}"
        yield message.format(time=timestamp, status=status,
            title=metadata["title"], info=info, duration=duration)

    def failure(self, log):
        metadata = log["metadata"]
        status = metadata["status"]
        duration = metadata["stop"] - metadata["start"]
        timestamp = datetime.datetime.fromtimestamp(log["timestamp"])
        info = "mem: %{:.6}, cpu: %{:.6}".format(log["mem"], log["cpu"])
        message = "{time} [{status}] {title} after {duration:.3f} seconds - {info}"
        yield message.format(time=timestamp, status=status,
            title=metadata["title"], info=info, duration=duration)


class Tree(Style):

    def _pre(self, log):
        metadata = log["metadata"]
        if not isinstance(metadata["title"], str):
            try:
                metadata["title"] = infer_title(metadata["title"])
            except:
                pass
        return log

    def started(self, log):
        content, metadata = log["content"], log["metadata"]
        indent = "|   " * metadata["depth"]
        timestamp = datetime.datetime.fromtimestamp(log["timestamp"])
        yield indent + "|-- {status}: {title}".format(**metadata)
        yield indent + "|   @ {0}".format(timestamp)
        if "reason" in content:
            yield indent + "|   | reason: {0}".format(content.pop("reason"))
        for k, v in content.items():
            yield indent + "|   | {0}: {1}".format(k, v)

    def working(self, log):
        content, metadata = log["content"], log["metadata"]
        indent = "|   " * (metadata["depth"] + 1)
        timestamp = datetime.datetime.fromtimestamp(log["timestamp"])
        yield indent + "|-- {status}: {title}".format(**metadata)
        yield indent + "|   @ {0}".format(timestamp)
        if "reason" in content:
            yield indent + "|   | reason: {0}".format(content.pop("reason"))
        for k, v in content.items():
            yield indent + "|   | {0}: {1}".format(k, v)

    def success(self, log):
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

    def failure(self, log):
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

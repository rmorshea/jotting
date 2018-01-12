import sys
import json
import datetime
import inspect


class Style(object):

    default = None

    def __call__(self, log):
        method = getattr(self, log["metadata"]["status"], self.default)
        if method is not None:
            lines = method(log)
            if lines and isinstance(lines, str):
                lines = [lines]
            else:
                lines = list(lines)
            if lines:
                return "\n".join(lines) + "\n"


class Raw(Style):

    def default(self, log):
        try:
            return json.dumps(log)
        except:
            content = {k: str(v) for k, v in log["content"].items()}
            return json.dumps(dict(log, content=content))


class Log(Style):

    def working(self, log):
        if log["content"]["reason"] is not None:
            metadata = log["metadata"]
            status = metadata["status"]
            timestamp = datetime.datetime.fromtimestamp(log["timestamp"])
            info = "mem: %{:.6}, cpu: %{:.6}".format(log["mem"], log["cpu"])
            yield "{time} [{status}] {reason} - {info}".format(
                time=timestamp, status=status,
                reason=log["content"]["reason"], info=info)

    def success(self, log):
        if log["content"]["reason"] is not None:
            metadata = log["metadata"]
            status = metadata["status"]
            duration = metadata["stop"] - metadata["start"]
            timestamp = datetime.datetime.fromtimestamp(log["timestamp"])
            info = "mem: %{:.6}, cpu: %{:.6}".format(log["mem"], log["cpu"])
            yield "{time} [{status}] {reason} after {duration:.3f} seconds - {info}".format(
                time=timestamp, status=status, duration=duration,
                reason=log["content"]["reason"], info=info)

    def failure(self, log):
        metadata = log["metadata"]
        status = metadata["status"]
        duration = metadata["stop"] - metadata["start"]
        timestamp = datetime.datetime.fromtimestamp(log["timestamp"])
        info = "mem: %{:.6}, cpu: %{:.6}".format(log["mem"], log["cpu"])
        yield "{time} [{status}] {reason} after {duration:.3f} seconds - {info}".format(
            time=timestamp, status=status, duration=duration,
            reason=log["content"]["reason"], info=info)


class Tree(Style):

    def started(self, log):
        content, metadata = log["content"], log["metadata"]
        indent = "|   " * metadata["depth"]
        timestamp = datetime.datetime.fromtimestamp(log["timestamp"])
        yield indent + "|-- {status}: {title}".format(**metadata)
        yield indent + "|   @ {0}".format(timestamp)
        for k, v in content.items():
            yield indent + "|   | {0}: {1}".format(k, v)

    def working(self, log):
        content, metadata = log["content"], log["metadata"]
        indent = "|   " * (metadata["depth"] + 1)
        timestamp = datetime.datetime.fromtimestamp(log["timestamp"])
        yield indent + "|-- {status}: {title}".format(**metadata)
        yield indent + "|   @ {0}".format(timestamp)
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
        if content["reason"] in content:
            del content["reason"]
        for k, v in content.items():
            yield indent + "    | {0}: {1}".format(k, v)

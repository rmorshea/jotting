import sys
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

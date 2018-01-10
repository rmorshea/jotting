import os
import json

class WriterMixin(object):

    def __init__(self, target, inbox):
        super().__init__()
        for attr in ("join", "get", "put", "task_done"):
            if not hasattr(inbox, attr):
                raise TypeError("Expected some type of joinable"
                    " queue that implements %r." % attr)
        self.inbox = inbox
        self.daemon = True
        if target is not None:
            self._target = target
        self.start()

    def __call__(self, log):
        message = self.serialize(log)
        self.inbox.put(message)

    def run(self):
        while True:
            message = self.inbox.get()
            try:
                self.write(message)
            except:
                raise
            finally:
                self.inbox.task_done()

    def serialize(self, log):
        if isinstance(log, str):
            return log
        else:
            try:
                return json.dumps(log)
            except:
                content = {k: str(v) for k, v in log["content"].items()}
                log["content"] = content
                return json.dumps(log)


    def write(self, message):
        if self._target is None:
            raise NotImlementedError()
        else:
            self._target(message)


class ToFileMixin(object):

    def __init__(self, filepath):
        self.filepath = os.path.realpath(os.path.expanduser(filepath))
        super().__init__()

    def write(self, message):
        with open(self.filepath, "a+") as f:
            f.write(message)

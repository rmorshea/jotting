import sys
import time
import json

from .. import utils


class paper(dict):

    configuration = {}
    _encoder = json.JSONEncoder

    def _writer(self, message):
        print(json.dumps(message, cls=self._encoder))

    def __init__(self, *args, **kwargs):
        self.metadata = {}
        self.configuration = self.configuration.copy()
        self.update(*args, **kwargs)

    def update(self, *args, **kwargs):
        for k, v in utils.merge({}, *args, **kwargs).items():
            if k.startswith("_"):
                if k == "_configuration":
                    raise ValueError("The name %r is a "
                        "reserved configuration key" % k)
                self.configuration[k[1:]] = v
            else:
                self.metadata[k] = v

    def copy(self, *args, **kwargs):
        new = type(self)()
        new.metadata = self.metadata.copy()
        new.configuration = self.configuration.copy()
        new.update(*args, **kwargs)
        return new

    def __call__(self, **content):
        if not self.metadata.get("status", False):
            raise TypeError("Cannot write unless used inside a function.")
        message = {"metadata": self.metadata, "content": content}
        message["metadata"]["timestamp"] = time.time()
        self._writer(message)

    def is_configured(self, name):
        return name in self.configuration

    def __getattribute__(self, name):
        if name.startswith("_") and name[1:] in self.configuration:
            return self.configuration[name[1:]]
        else:
            return super().__getattribute__(name)

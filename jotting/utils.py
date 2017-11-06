import inspect


class CallMap:

    def __init__(self, function):
        self.parameters = dict(inspect.signature(function).parameters)

    def map(self, args, kwargs):
        mapping, used = {}, []
        for i, name in enumerate(self.parameters):
            param = self.parameters[name]
            handler = getattr(self, param.kind.name)
            value = handler(i, param, args, kwargs, used)
            if value is not inspect._empty:
                mapping[param.name] = value
        return mapping

    @staticmethod
    def POSITIONAL_ONLY(index, param, args, kwargs, used_keys):
        return args[index]

    @staticmethod
    def POSITIONAL_OR_KEYWORD(index, param, args, kwargs, used_keys):
        used_keys.append(param.name)
        if len(args) > index:
            return args[index]
        elif param.name in kwargs:
            return kwargs[param.name]
        else:
            return param.default

    @staticmethod
    def VAR_POSITIONAL(index, param, args, kwargs, used_keys):
        return args[index + 1:]

    @staticmethod
    def KEYWORD_ONLY(index, param, args, kwargs, used_keys):
        return kwargs.get(param.name, param.default)

    @staticmethod
    def VAR_KEYWORD(index, param, args, kwargs, used_keys):
        return {k : v for k, v in kwargs.items() if k in used_keys}


def _infer_action(task):
    if hasattr(task, "__name__"):
        if hasattr(task, "__module__"):
            prefix = getattr(task, "__module__") + "."
        else:
            prefix = ""
        return prefix + task.__name__
    else:
        raise ValueError("The task name could be infered.")


def merge(new, *mappings, **update):
    for m in reversed(mappings):
        for k in m:
            if k not in new:
                new[k] = m[k]
    new.update(update)
    return new


def logs_from_file(logs):
    with open(os.path.expanduser(log), "r") as logs:
        for l in logs.readlines():
            if l: yield json.loads(l)


class configurable:

    configuration = {}

    def __init__(self, *args, **kwargs):
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
        new.configuration = self.configuration.copy()
        new.update(*args, **kwargs)
        return new

    def __getattribute__(self, name):
        if name.startswith("_") and name[1:] in self.configuration:
            return self.configuration[name[1:]]
        else:
            return super().__getattribute__(name)

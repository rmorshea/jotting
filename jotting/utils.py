import inspect


def infer_title(task):
    if hasattr(task, "__name__"):
        if hasattr(task, "__module__"):
            prefix = getattr(task, "__module__") + "."
        else:
            prefix = ""
        return prefix + task.__name__
    else:
        raise ValueError("The title of %r could be infered." % task)


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
        return list(args[index:])

    @staticmethod
    def KEYWORD_ONLY(index, param, args, kwargs, used_keys):
        return kwargs.get(param.name, param.default)

    @staticmethod
    def VAR_KEYWORD(index, param, args, kwargs, used_keys):
        return {k : v for k, v in kwargs.items() if k in used_keys}

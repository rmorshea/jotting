import sys
import types
import inspect

if sys.version_info > (3, 3):
    from inspect import signature

    def pkind(p):
        return p.kind.name
else:
    from funcsigs import signature

    def pkind(p):
        return p.kind._name


def to_title(x, inputs):
    if isinstance(x, str):
        title = x.format(**inputs)
    else:
        try:
            x = enclosed(x)
        except TypeError:
            title = str(x)
        else:
            title = "%s.%s" % (
                x.__module__,
                x.__name__)
    return title


def enclosed(x):
    """Return a function that was decorated by another."""
    if inspect.isclass(x):
        return x
    elif isinstance(x, types.MethodType):
        x = x.__func__
    elif not isinstance(x, types.FunctionType):
        raise TypeError("%r is not a function or class." % x)
    name = x.__name__
    module = x.__module__
    candidates = []
    if x.__closure__:
        for cell in x.__closure__:
            contents = cell.cell_contents
            if callable(contents):
                if name == getattr(contents, "__name__", None):
                    if module == getattr(contents, "__module__", None):
                        candidates.append(enclosed(contents))
        if len(candidates) == 0:
            raise TypeError("Bad wrapping - make sure to use functools.wraps")
        elif len(candidates) > 1:
            listed = ", ".join(map(repr, candidates))
            raise TypeError("Bad wrapping - cannot distinguish between %s" % listed)
        else:
            return candidates[0]
    else:
        return x


class CallMap(object):

    def __init__(self, function):
        self.parameters = dict(signature(function).parameters)

    def map(self, args, kwargs):
        mapping, used = {}, []
        for i, name in enumerate(self.parameters):
            param = self.parameters[name]
            handler = getattr(self, pkind(param))
            value = handler(i, param, args, kwargs, used)
            if value is not param.empty:
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


class Switch(object):

    def _switch(self, log, *args, **kwargs):
        status = log["metadata"]["status"]
        method = getattr(self, "_" + status, None) or self._default
        return method(log, *args, **kwargs)

    def default(self, *args, **kwargs):
        pass

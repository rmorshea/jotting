import inspect
from enum import Enum
from functools import wraps

from .. import utils
from .book import book


class statuses(Enum):
    failure = 0
    started = 1
    running = 2
    success = 3


class Strike(Exception): pass


def strike(message):
    raise Strike(message)


def worthy(action=None, **notes):

    def setup(function):
        if callable(action):
            notes["action"] = utils._infer_action(function)
        elif isinstance(action, str):
            notes["action"] = action

        cm = utils.CallMap(function)

        if inspect.iscoroutinefunction(function):
            @wraps(function)
            async def notetaker(*args, **kwargs):
                with book(kwargs.pop("notepad", {}), notes) as notepad:
                    inputs = cm.map(args, kwargs)
                    action = notepad.metadata["action"]
                    notepad.update(action=action.format(**inputs))
                    started = notepad.copy(status=statuses.started.name)
                    running = notepad.copy(status=statuses.running.name)
                    success = notepad.copy(status=statuses.success.name)
                    failure = notepad.copy(status=statuses.failure.name)
                    if "notepad" in cm.parameters:
                        kwargs["notepad"] = running
                    started(**inputs)
                    try:
                        product = await function(*args, **kwargs)
                    except Exception as error:
                        failure(error=str(error))
                        if not isinstance(error, Strike):
                            raise
                    else:
                        success(returned=str(product))
                        return product
        else:
            @wraps(function)
            def notetaker(*args, **kwargs):
                with book(kwargs.pop("notepad", {}), notes) as notepad:
                    inputs = cm.map(args, kwargs)
                    action = notepad.metadata["action"]
                    notepad.update(action=action.format(**inputs))
                    started = notepad.copy(status=statuses.started.name)
                    running = notepad.copy(status=statuses.running.name)
                    success = notepad.copy(status=statuses.success.name)
                    failure = notepad.copy(status=statuses.failure.name)
                    if "notepad" in cm.parameters:
                        kwargs["notepad"] = running
                    started(**inputs)
                    try:
                        product = function(*args, **kwargs)
                    except Exception as error:
                        failure(error=str(error))
                        if not isinstance(error, Strike):
                            raise
                    else:
                        success(returned=str(product))
                        return product
        return notetaker

    if action is None or isinstance(action, str):
        return setup
    else:
        return setup(action)

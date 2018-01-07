# Jotting

Logs that explain when, where, and why things happen.

> Jotting was heavily influenced by [`eliot`](https://eliot.readthedocs.io/).

## Install

Install `jotting` with `pip`:

```bash
$ pip install jotting
```

## Quickstart

The beauty of `jotting` is a simple and intuitive interface that doesn't clutter code. All you need to do to get started logging events is to decorate a function with `book.mark`:

```python
from jotting import book


@book.mark
def function(a, b):
    book.write(debug="about to finish")
    return a + b

c = function(1, 2)
```

By default this will print:

```
|-- started: __main__.function
|   @ 2018-01-07 11:14:01.650153
|   | a: 1
|   | b: 2
|   |-- working: __main__.function
|   |   @ 2018-01-07 11:14:01.650498
|   |   | debug: about to finish
|   `-- success: __main__.function
|       @ 2018-01-07 11:14:01.650583
|       | returned: 3
```

However where this text is logged, and how its format are all configurable.

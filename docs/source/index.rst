Jotting
=======

:mod:`jotting` is a log system for Python 2 and 3 that can be used to record
the causal history of an asynchronous or distributed system. These histories
are composed of actions which, once "started", will begin "working", potentially
spawn other actions, and eventually end as a "success" or "failure". In the end
you're left with a breadcrumb trail of information that you can use to squash
bugs with minimal boilerplate.

.. toctree::
    :maxdepth: 1

    pages/install
    pages/quickstart
    pages/examples
    pages/api

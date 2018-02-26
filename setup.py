import os
import sys
import subprocess
from os import path
from glob import glob
from distutils.core import setup
from setuptools import find_packages

#-----------------------------------------------------------------------------
# Project
#-----------------------------------------------------------------------------

url = "https://github.com/rmorshea/jotting"
project = "jotting"
version = "0.2.0"
author = "Ryan Morshead"
email = "ryan.morshead@gmail.com"
summary = "causally related logging messages"

description = """
Jotting
-------

Logs that explain when, where, and why things happen.

``jotting`` is a log system for Python that can be used to record the causal
history of an asynchronous or distributed system. These histories are composed
of actions which, once "started", will begin "working", potentially spawn other
actions, and eventually end as a "success" or "failure". In the end you're left
with a breadcrumb trail of information that you can use to squash bugs with
minimal boilerplate.

Jotting was heavily inspired by ``eliot`` (https://eliot.readthedocs.io/).
"""

#-----------------------------------------------------------------------------
# Packages
#-----------------------------------------------------------------------------

packages = find_packages(project)

#-----------------------------------------------------------------------------
# Base Paths
#-----------------------------------------------------------------------------

here = path.abspath(path.dirname(__file__))
root = path.join(here, project)

#-----------------------------------------------------------------------------
# Finalize Parameters
#-----------------------------------------------------------------------------

if sys.version_info < (3, 5):
    requires = ["funcsigs"]
else:
    requires = []

parameters = dict(
    url=url,
    name=project,
    version=version,
    author=author,
    author_email=email,
    description=summary,
    long_description=description,
    packages=find_packages(),
    python_requires = ">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*",
    install_requries=requires,
    classifiers = [
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)

#-----------------------------------------------------------------------------
# Setup
#-----------------------------------------------------------------------------

if __name__ == "__main__":
    setup(**parameters)

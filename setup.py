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

project = "jotting"
version = "0.0.4"
author = "Ryan Morshead"
email = "ryan.morshead@gmail.com"
summary = "causally related logging messages"

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

if sys.version_info >= (3, 5):
    requires = ["psutil"]
else:
    requires = ["psutil", "funcsigs"]

parameters = dict(
    name=project,
    version=version,
    author=author,
    author_email=email,
    description=summary,
    packages=find_packages(),
    python_requires = ">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*",
    install_requries=requires,
)

#-----------------------------------------------------------------------------
# Setup
#-----------------------------------------------------------------------------

if __name__ == "__main__":
    setup(**parameters)

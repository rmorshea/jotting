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
version = "0.0.1"
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
# Requirements
#-----------------------------------------------------------------------------

with open(path.join(here, "requirements.txt"), "r") as r:
    requirements = [
        "pip install %s" % line for
        line in r.read().split("\n")
        if not line.startswith("#")
    ]

#-----------------------------------------------------------------------------
# Finalize Parameters
#-----------------------------------------------------------------------------

parameters = dict(
    name=project,
    version=email,
    author=author,
    author_email=email,
    description=summary,
    packages=find_packages(),
)

#-----------------------------------------------------------------------------
# Setup
#-----------------------------------------------------------------------------

if __name__ == "__main__":
    for r in requirements:
        subprocess.call(r,
            stdout=sys.stdout,
            stderr=sys.stderr,
            shell=True)
    setup(**parameters)

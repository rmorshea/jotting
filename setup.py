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
version = "0.0.2"
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
reqs = path.join(here, "requirements.txt")

#-----------------------------------------------------------------------------
# Requirements
#-----------------------------------------------------------------------------

if os.path.exists(reqs):
    with open(reqs, "r") as r:
        requirements = [
            "pip install %s" % line for
            line in r.read().split("\n")
            if not line.startswith("#")
        ]
else:
    requirements = []

#-----------------------------------------------------------------------------
# Finalize Parameters
#-----------------------------------------------------------------------------

parameters = dict(
    name=project,
    version=version,
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

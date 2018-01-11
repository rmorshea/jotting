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
requirements = path.join(here, "requirements.txt")

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
    install_requries=["psutil"]
)

#-----------------------------------------------------------------------------
# Setup
#-----------------------------------------------------------------------------

if __name__ == "__main__":
    setup(**parameters)

#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
import sys

try:
    from setuptools import find_packages, setup, Command
except ImportError:
    from distutils.core import find_packages, setup, Command


here = os.path.abspath(os.path.dirname(__file__))

DESCRIPTION = "Simple VTXX compatible terminal emulator."

try:
    LONG_DESCRIPTION = open(os.path.join(here, "README.rst")).read()
except IOError:
    LONG_DESCRIPTION = ""


CLASSIFIERS = (
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Operating System :: OS Independent",
    "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.6",
    "Topic :: Terminals :: Terminal Emulators/X Terminals",
)


class PyTest(Command):
    """Unfortunately :mod:`setuptools` support only :mod:`unittest`
    based tests, thus, we have to overider build-in ``test`` command
    to run :mod:`pytest`.

    .. note::

       Please pack your tests, using ``py.test --genscript=runtests.py``
       before commiting, this will eliminate `pytest` dependency.
    """
    user_options = []
    initialize_options = finalize_options = lambda self: None

    def run(self):
        errno = subprocess.call([sys.executable, "runtests.py"])
        raise SystemExit(errno)


setup(name="vt102",
      version="0.3.7",
      packages=find_packages(exclude=["tests"]),
      cmdclass={"test": PyTest},
      platforms=["any"],

      author="Sam Gibson",
      author_email="sam@ifdown.net",
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      classifiers=CLASSIFIERS,
      keywords=["vt102", "terminal emulator"],
      url="https://github.com/samfoo/vt102",
)

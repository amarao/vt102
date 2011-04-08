# -*- coding: utf-8 -*-

import os

try:
    from setuptools import find_packages, setup
except ImportError:
    from distutils.core import find_packages, setup


here = os.path.abspath(os.path.dirname(__file__))

DESCRIPTION = "Simple vt102 emulator -- useful for screen scraping."

try:
    LONG_DESCRIPTION = open(os.path.join(here, "README.rst")).read()
except IOError:
    pass


CLASSIFIERS = (
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Operating System :: OS Independent",
    "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
    "Programming Language :: Python",
    "Topic :: Terminals :: Terminal Emulators/X Terminals",
)

setup(name="vt102",
      version="0.3.4",
      packages=find_packages(),
      platforms=["any"],

      author="Sam Gibson",
      author_email="sam@ifdown.net",
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      classifiers=CLASSIFIERS,
      keywords=["vt102", "terminal emulator", "screen scraper"],
      url="https://github.com/samfoo/vt102",
      test_suite="tests",
)

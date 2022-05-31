import sys
from setuptools import setup

if sys.version_info < (3, 8):
    raise RuntimeError("requires Python 3.8+")

setup()

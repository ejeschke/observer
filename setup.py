#! /usr/bin/env python
#
from distutils.core import setup
import os

srcdir = os.path.dirname(__file__)

try:  # Python 3.x
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:  # Python 2.x
    from distutils.command.build_py import build_py

setup(
    name = "observer",
    version = "0.1",
    author = "Dan Magee",
    author_email = "magee@ucolick.org",
    description = ("Observer is a Python package for computing nightly almanacs and plotting airmass charts for astronomical targets."),
    license = "BeerWare",
    keywords = "astronomy almanacs airmass",
    url = "http://www.ucolick.org/~magee/observer/",
    packages = ['observer', ],
    package_data = { },
    scripts = [],
    classifiers = [
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Topic :: Scientific/Engineering :: Astronomy",
    ],
    cmdclass={'build_py': build_py}
)


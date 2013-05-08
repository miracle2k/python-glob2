#!/usr/bin/env python
import os
from setuptools import setup, find_packages


# Figure out the version
import re
here = os.path.dirname(os.path.abspath(__file__))
version_re = re.compile(
    r'__version__ = (\(.*?\))')
fp = open(os.path.join(here, 'src/glob2', '__init__.py'))
version = None
for line in fp:
    match = version_re.search(line)
    if match:
        version = eval(match.group(1))
        break
else:
    raise Exception("Cannot find version in __init__.py")
fp.close()


setup(
    name = 'glob2',
    version = ".".join(map(str, version)),
    description = 'Version of the glob module that can capture patterns '+
                  'and supports recursive wildcards',
    author = 'Michael Elsdoerfer',
    author_email = 'michael@elsdoerfer.com',
    url = 'http://github.com/miracle2k/python-glob2/',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
        ],
    packages = find_packages('src'),
    package_dir = {'': 'src'},
)

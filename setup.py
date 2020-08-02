#!/usr/bin/python

# Copyright 2011 Tomo Krajina
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import gpxpy
import sys

from setuptools import setup # type: ignore

if sys.version_info < (3, 6):
    sys.exit('Sorry, Python < 3.6 is not supported')

with open('README.md') as f:
    long_description = f.read()

setup(
    name='gpxpy',
    version=gpxpy.__version__,
    description='GPX file parser and GPS track manipulation library',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='Apache License, Version 2.0',
    author='Tomo Krajina',
    author_email='tkrajina@gmail.com',
    url='https://github.com/tkrajina/gpxpy',
    package_data={"gpxpy": ["py.typed"]},
    packages=['gpxpy', ],
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    scripts=['gpxinfo'],
)

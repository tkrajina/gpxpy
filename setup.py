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

import distutils.core as mod_distutilscore

mod_distutilscore.setup(
    name='gpxpy',
    version='1.0.0',
    description='GPX file parser and GPS track manipulation library',
    license='Apache License, Version 2.0',
    author='Tomo Krajina',
    author_email='tkrajina@gmail.com',
    url='http://www.trackprofiler.com/gpxpy/index.html',
    packages=['gpxpy', ],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
    scripts=['gpxinfo']
)

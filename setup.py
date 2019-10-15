# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import os
from setuptools import setup, find_packages, Command
from distutils import log

setup(
    name='gfdiffbrowsers',
    version='0.1.6',
    author="Marc Foley",
    author_email="marc@mfoley.uk",
    description="Diff two sets of fonts in different browsers",
    url="https://github.com/googlefonts/diffbrowsers",
    license="Apache Software License 2.0",
    package_dir={"": "Lib"},
    packages=find_packages("Lib"),
    entry_points={
        "console_scripts": [
            "gfdiffbrowsers = diffbrowsers.__main__:main"
        ],
    },
    scripts=[
        os.path.join('bin', 'test_gf_vf.py'),
        os.path.join('bin', 'test_gf_autohint.py'),
        os.path.join('bin', 'test_gf_exhaustive.py'),
        os.path.join('bin', 'viz_diffenator.py')
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        "Environment :: Console",
        "Environment :: Other Environment",
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Multimedia :: Graphics :: Graphics Conversion',
        'Topic :: Multimedia :: Graphics :: Editors :: Vector-Based',
    ],
    install_requires=[
        "Pillow>=5.4.1",
        "pybrowserstack-screenshots==0.1",
        "requests",
    ],
)

# -*- coding: utf-8 -*-

import sys
from setuptools import setup, find_packages

if sys.version_info[0] < 3:
    with open('README.md', 'r') as fh:
        long_description = fh.read()
else:
    with open('README.md', 'r', encoding='utf-8') as fh:
        long_description = fh.read()

setup(
    name='core-lib-python',
    version='1.0.0',
    description='The core library for python SDKs provided by APIMatic',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='APIMatic',
    author_email='support@apimatic.io',
    url='https://apimatic.io',
    packages=find_packages(),
    install_requires=[
        'jsonpickle~=1.4, >= 1.4.1',
        'python-dateutil~=2.8.1',
        'enum34~=1.1, >=1.1.10'
    ],
    tests_require=[
        'pytest~=7.1.3',
        'pytest-cov~=3.0.0',
        'pytest-mock~=3.8.2'
    ]
)
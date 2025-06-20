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
    name='apimatic-core',
    version='0.2.21',
    description='A library that contains core logic and utilities for '
                'consuming REST APIs using Python SDKs generated by APIMatic.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='APIMatic',
    author_email='support@apimatic.io',
    license='MIT',
    url='https://github.com/apimatic/core-lib-python',
    packages=find_packages(),
    install_requires=[
        'apimatic-core-interfaces~=0.1.0',
        'jsonpickle~=3.3.0',
        'python-dateutil~=2.8',
        'requests~=2.31',
        'setuptools>=68.0.0',
        'jsonpointer~=2.3'
    ],
    tests_require=[
        'pytest~=7.2.2',
        'pytest-cov~=4.0.0'
    ]
)

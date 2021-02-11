#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()


setup(
    author="Eric Truett",
    author_email='eric@erictruett.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="pyt",
    license="MIT license",
    long_description=readme,
    keywords='nbafantasy',
    name='nbapr',
    packages=find_packages(),
    url='https://github.com/sansbacon/nbapr',
    version='0.1.0',
    zip_safe=False,
)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

def run():
    setup(
        author="Eric Truett",
        author_email='eric@erictruett.com',
        license="MIT license",
        name='nbapr',
        packages=find_packages(),
        entry_points={
            'console_scripts': ['sim=scripts.runfbasim:run', 'update=scripts.update_datafiles:run'],
        },
        url='https://github.com/sansbacon/nbapr',
        version='0.1.0',
        zip_safe=False,
    )


if __name__ == '__main__':
    run()
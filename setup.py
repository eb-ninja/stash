#!/usr/bin/env python

from setuptools import setup, find_packages


requirements = [
    'Flask == 0.10',
    'flask-hype == 0.1.4',
    'kazoo == 2.2.1',
    'pilo == 0.4.0',
    'coid == 0.1.1',
    'iso8601 == 0.1.10',
]


setup(
    name='stash',
    version='0.0.1',
    url='https://www.github.com/eb-ninja/stash',
    author='cieplak@eventbrite.com',
    description='inventory reservation service',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    install_requires=requirements,
    tests_require=['nosetests', 'mock>=0.8'],
)

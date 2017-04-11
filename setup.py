
from setuptools import setup, find_packages

import edenred

setup(
    name='edenred-payments',
    version=edenred.__VERSION__,
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['requests', 'pycrypto'],
    test_suite='nose.collector',
    tests_require=['nose', 'mock'],
)

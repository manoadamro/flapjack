# coding: utf-8

import setuptools

NAME = 'flapjack'
VERSION = '0.0.0'
REQUIRES = [
    'flask',
    'flask_sqlalchemy',
    'waitress',
    'flapi-jwt @ https://github.com/manoadamro/flapi-jwt/tarball/master#egg=flapi-jwt',
    'flapi-schema @ https://github.com/manoadamro/flapi-schema/tarball/master#egg=flapi-schema',
]


setuptools.setup(
    name=NAME,
    version=VERSION,
    install_requires=REQUIRES,
    packages=setuptools.find_packages()
)

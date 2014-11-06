# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
    name='pygamepad',
    version='0.0.1',
    author='Simon Dickreuter',
    author_email='Simon.Dickreuter@uni-tuebingen.de',
    packages=['pygamepad',],
    description='Python module for commanding PI P545 Piezo Stage. This software is not associated with PI. Use it at your own risk.',
    long_description=open('README.md').read(),
    requires=['python (>= 2.7)'],
)

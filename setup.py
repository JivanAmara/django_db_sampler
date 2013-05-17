# coding=utf-8
""" @brief Distutils setup file.
    @author jivan
    @since Jun 15, 2012
"""
from __future__ import unicode_literals, print_function, division
from distutils.core import setup

setup(
    name='django_db_sampler',
    description='Utility to easily extract specific models from a database with their dependencies.  Especially useful for creating fixtures.',
    author='Jivan Amara',
    author_email='Development@JivanAmara.net',
    url='https://github.com/JivanAmara/django_db_sampler',
    version='0.21',
    py_modules=['db_sampler_script'],
)

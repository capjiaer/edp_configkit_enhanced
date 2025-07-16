#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Setup script for edp_configkit_enhanced
"""

from setuptools import setup, find_packages
import os

# Read the contents of your README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open(os.path.join(this_directory, 'requirements.txt'), encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='edp_configkit_enhanced',
    version='0.2.0',
    author='ConfigKit Team',
    author_email='configkit@example.com',
    description='Enhanced ConfigKit - A library for configuration transformation between Python and Tcl',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/edp_configkit_enhanced',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Configuration',
        'Topic :: Text Processing :: Markup :: XML',
    ],
    python_requires='>=3.6',
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'flake8>=3.8',
            'black>=20.8b1',
            'mypy>=0.812',
        ],
        'docs': [
            'sphinx>=3.0',
            'sphinx-rtd-theme>=0.5',
        ],
    },
    include_package_data=True,
    keywords='configuration config yaml tcl conversion transformation',
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/edp_configkit_enhanced/issues',
        'Source': 'https://github.com/yourusername/edp_configkit_enhanced',
        'Documentation': 'https://github.com/yourusername/edp_configkit_enhanced/blob/main/README.md',
    },
) 
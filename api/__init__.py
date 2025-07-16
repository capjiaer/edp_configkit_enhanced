#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
High-level API for configkit.

This package contains high-level API functions for file conversion operations:
- file_converters: Mixed file format conversion functions
"""

from .file_converters import (
    files2dict, files2tclfile, files2yamlfile,
    tclfiles2yamlfile, yamlfiles2tclfile
)

__all__ = [
    # Mixed file operations
    'files2dict',
    'files2tclfile', 
    'files2yamlfile',
    
    # Single format conversions
    'tclfiles2yamlfile',
    'yamlfiles2tclfile',
] 
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Core modules for configkit.

This package contains the core functionality modules:
- dict_operations: Dictionary manipulation and merging
- value_converter: Python/Tcl value format conversion
- tcl_interpreter: Tcl interpreter interaction
"""

from .dict_operations import merge_dict, yamlfiles2dict
from .value_converter import value_format_py2tcl, value_format_tcl2py, detect_tcl_list
from .tcl_interpreter import (
    create_tcl_interp, dict2tclinterp, tclinterp2dict, tclfiles2tclinterp, 
    tclinterp2tclfile, _write_tcl_vars_to_file
)

__all__ = [
    # Dictionary operations
    'merge_dict',
    'yamlfiles2dict',
    
    # Value conversion
    'value_format_py2tcl',
    'value_format_tcl2py', 
    'detect_tcl_list',
    
    # Tcl interpreter operations
    'create_tcl_interp',
    'dict2tclinterp',
    'tclinterp2dict',
    'tclfiles2tclinterp',
    'tclinterp2tclfile',
] 
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Dictionary operations for configkit.

This module provides functions for dictionary manipulation and merging,
as well as loading YAML files into dictionaries.

本模块提供字典操作和合并功能，以及将YAML文件加载到字典中。
"""

import os
import yaml
from typing import Dict, Optional
from tkinter import Tcl


def merge_dict(dict1: Dict, dict2: Dict) -> Dict:
    """
    Recursively merge two dictionaries. If there are conflicts, values from dict2 will override dict1.
    For lists, values are appended rather than replaced.

    Args:
        dict1: First dictionary
        dict2: Second dictionary to merge into dict1

    Returns:
        Merged dictionary
    """
    result = dict1.copy()

    for key, value in dict2.items():
        if key in result:
            if isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge nested dictionaries
                result[key] = merge_dict(result[key], value)
            elif isinstance(result[key], list) and isinstance(value, list):
                # For lists, append items from dict2 to dict1
                result[key] = result[key] + value
            else:
                # For other types, dict2 values override dict1
                result[key] = value
        else:
            # Key doesn't exist in dict1, just add it
            result[key] = value

    return result


def yamlfiles2dict(*yaml_files: str, variable_interp: Optional[Tcl] = None) -> Dict:
    """
    Convert one or more YAML files to a merged dictionary.
    
    Args:
        *yaml_files: One or more paths to YAML files
        variable_interp: Optional Tcl interpreter for variable resolution.
                        If provided, variables like $var in YAML values will be resolved.
                        If None, no variable resolution is performed (default behavior).

    Returns:
        Dictionary containing merged content from all YAML files

    Raises:
        FileNotFoundError: If any of the YAML files doesn't exist
        yaml.YAMLError: If there's an error parsing any YAML file
        
    Example:
        # Basic usage (no variable resolution)
        config = yamlfiles2dict("config.yaml")
        
        # With variable resolution using new interpreter
        from .tcl_interpreter import create_tcl_interp
        interp = create_tcl_interp()
        config = yamlfiles2dict("config.yaml", variable_interp=interp)
        
        # With pre-configured interpreter
        interp = create_tcl_interp()
        interp.eval("set env production")
        config = yamlfiles2dict("config.yaml", variable_interp=interp)
    """
    # Load and merge YAML files normally
    result = {}
    for yaml_file in yaml_files:
        if not os.path.exists(yaml_file):
            raise FileNotFoundError(f"YAML file not found: {yaml_file}")

        with open(yaml_file, 'r', encoding='utf-8') as f:
            yaml_dict = yaml.safe_load(f)
            if yaml_dict:  # Handle empty YAML files
                result = merge_dict(result, yaml_dict)

    # If no variable resolution requested, return as-is
    if variable_interp is None:
        return result
    
    # Import here to avoid circular dependency
    from .tcl_interpreter import dict2tclinterp, tclinterp2dict
    
    # Use Tcl for variable resolution
    dict2tclinterp(result, variable_interp)
    return tclinterp2dict(variable_interp) 
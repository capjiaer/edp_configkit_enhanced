#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Value conversion utilities for configkit.

This module provides functions for converting values between Python and Tcl formats.
It handles type conversion for basic types (int, float, bool, string) as well as
complex structures (lists, dictionaries).

本模块提供Python和Tcl格式之间的值转换功能。
它处理基本类型（int、float、bool、string）以及复杂结构（list、dict）的类型转换。
"""

from tkinter import Tcl
from typing import Any


def value_format_py2tcl(value: Any) -> str:
    """
    Convert Python value to Tcl format.

    Args:
        value: Python value to convert

    Returns:
        String representation of the value in Tcl format
    """
    if value is None:
        return '""'
    elif isinstance(value, bool):
        return "1" if value else "0"
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, list):
        # Convert list to Tcl list format: [list elem1 elem2 ...]
        elements = [value_format_py2tcl(item) for item in value]
        return f"[list {' '.join(elements)}]"
    elif isinstance(value, dict):
        # For dictionaries, we'll use Tcl's dict create command
        items = []
        for k, v in value.items():
            items.append(f"{value_format_py2tcl(k)} {value_format_py2tcl(v)}")
        return f"[dict create {' '.join(items)}]"
    else:
        # For strings, escape any special characters
        value_str = str(value)
        # If the string contains spaces or special characters, we need to handle it properly
        if any(c in value_str for c in ' \t\n\r{}[]$"\\'):
            # Use braces for complex strings to preserve literal meaning
            return f"{{{value_str}}}"
        return value_str


def detect_tcl_list(tcl_value: str, var_name: str = "") -> bool:
    """
    Detect if a Tcl string value should be interpreted as a list.

    This function checks if a string value from Tcl should be converted to a Python list.
    It looks for patterns like space-separated numbers that likely represent a list.

    Args:
        tcl_value: Tcl value as a string
        var_name: Optional variable name for context-aware detection

    Returns:
        True if the value should be interpreted as a list, False otherwise
    """
    # If it's explicitly a Tcl list, it's already handled elsewhere
    if tcl_value.startswith("[list ") and tcl_value.endswith("]"):
        return False

    # If it's enclosed in braces, it's a complex string, not a list
    if tcl_value.startswith("{") and tcl_value.endswith("}"):
        return False

    # If it doesn't contain spaces, it's not a list
    if " " not in tcl_value:
        return False

    # Variable name hints - if the name suggests it's a list
    list_hint_names = ["list", "array", "items", "elements", "values"]
    is_likely_list_by_name = var_name and any(hint in var_name.lower() for hint in list_hint_names)

    # Split by spaces
    items = tcl_value.split()

    # If all items are numbers, it's likely a list of numbers
    all_numbers = True
    for item in items:
        try:
            float(item)
        except ValueError:
            all_numbers = False
            break

    if all_numbers and len(items) > 1:
        return True

    # Be more conservative with non-numeric items
    # Only consider it a list if the variable name suggests it's a list
    # or if it has a very specific pattern
    if is_likely_list_by_name and len(items) > 1:
        return True

    return False


def value_format_tcl2py(tcl_value: str) -> Any:
    """
    Convert Tcl value to Python format.

    Args:
        tcl_value: Tcl value as a string

    Returns:
        Python representation of the Tcl value
    """
    # Use Tcl interpreter to evaluate and convert the value
    interp = Tcl()

    # Handle empty string
    if not tcl_value or tcl_value == '""':
        return None

    # Try to interpret as a number
    try:
        if '.' in tcl_value:
            return float(tcl_value)
        else:
            return int(tcl_value)
    except ValueError:
        pass

    # Handle boolean values
    if tcl_value == "1" or tcl_value.lower() == "true":
        return True
    elif tcl_value == "0" or tcl_value.lower() == "false":
        return False

    # Handle explicit Tcl lists
    if tcl_value.startswith("[list ") and tcl_value.endswith("]"):
        list_content = tcl_value[6:-1].strip()
        if not list_content:
            return []

        # Use Tcl to properly parse the list
        result = interp.eval(f"return {tcl_value}")
        # Convert the result to a Python list
        return [value_format_tcl2py(item) for item in interp.splitlist(result)]

    # Check if the string value should be interpreted as a list
    if detect_tcl_list(tcl_value):
        # Split the string and convert each item
        items = interp.splitlist(tcl_value)
        return [value_format_tcl2py(item) for item in items]

    # Handle dictionaries
    if tcl_value.startswith("[dict create ") and tcl_value.endswith("]"):
        dict_content = tcl_value[12:-1].strip()
        if not dict_content:
            return {}

        try:
            # Use Tcl to properly parse the dictionary
            result = interp.eval(f"return {tcl_value}")
            # Convert the result to a Python dict
            result_dict = {}
            items = interp.splitlist(result)
            for i in range(0, len(items), 2):
                if i+1 < len(items):
                    key = items[i]
                    value = items[i+1]

                    # Handle nested dictionaries
                    if value.startswith("[dict create ") and value.endswith("]"):
                        py_key = value_format_tcl2py(key)
                        py_value = value_format_tcl2py(value)
                        result_dict[py_key] = py_value
                    else:
                        py_key = value_format_tcl2py(key)
                        py_value = value_format_tcl2py(value)
                        result_dict[py_key] = py_value
            return result_dict
        except Exception:
            # If there's an error parsing the dict, return as string
            return tcl_value

    # For other values, return as string
    return tcl_value 
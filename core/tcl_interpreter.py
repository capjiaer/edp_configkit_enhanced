#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tcl interpreter operations for configkit.

This module provides functions for interacting with Tcl interpreters,
including converting between Python dictionaries and Tcl variables,
and loading/saving Tcl files.

本模块提供与Tcl解释器交互的功能，包括Python字典与Tcl变量间的转换，
以及Tcl文件的加载和保存。
"""

import os
from tkinter import Tcl
from typing import Dict, List, Any, Optional

from .value_converter import value_format_py2tcl, value_format_tcl2py


def create_tcl_interp() -> Tcl:
    """
    Create a new Tcl interpreter and record its default variables.
    
    Returns:
        Tcl interpreter with default variables recorded in _configkit_default_vars attribute
    """
    interp = Tcl()
    # Record default variables that exist in a fresh interpreter
    default_vars = set(interp.eval("info vars").split())
    # Store as an attribute on the interpreter object
    interp._configkit_default_vars = default_vars
    return interp


def dict2tclinterp(data: Dict, interp: Optional[Tcl] = None) -> Tcl:
    """
    Convert a Python dictionary to Tcl variables in a Tcl interpreter.
    Also records type information for proper conversion back to Python.

    Args:
        data: Dictionary to convert
        interp: Optional Tcl interpreter to use. If None, a new one will be created.

    Returns:
        Tcl interpreter with variables set
    """
    if interp is None:
        interp = create_tcl_interp()

    # Initialize a special array to store type information
    interp.eval("array set __configkit_types__ {}")

    def _set_tcl_var(name: str, value: Any, parent_keys: List[str] = None):
        if parent_keys is None:
            parent_keys = []

        if isinstance(value, dict):
            for k, v in value.items():
                new_keys = parent_keys + [k]
                _set_tcl_var(name, v, new_keys)
        else:
            tcl_value = value_format_py2tcl(value)

            # Record type information
            type_key = name
            if parent_keys:
                type_key = f"{name}({','.join(parent_keys)})"

            # Store the Python type
            if isinstance(value, list):
                interp.eval(f"set __configkit_types__({type_key}) list")
            elif isinstance(value, bool):
                interp.eval(f"set __configkit_types__({type_key}) bool")
            elif value is None:
                interp.eval(f"set __configkit_types__({type_key}) none")
            elif isinstance(value, (int, float)):
                interp.eval(f"set __configkit_types__({type_key}) number")
            else:
                interp.eval(f"set __configkit_types__({type_key}) string")

            # Check if this variable name conflicts with default Tcl variables
            if hasattr(interp, '_configkit_default_vars') and name in interp._configkit_default_vars:
                # For any default variable (array or not), unset it first to allow user override
                try:
                    interp.eval(f"unset {name}")
                except:
                    pass  # If unset fails, that's okay, we'll try to set anyway
                # Use original name - user should be able to override any default variable
                safe_name = name
            else:
                # Use original name for user variables
                safe_name = name
            
            if not parent_keys:
                # Simple variable
                interp.eval(f"set {safe_name} {tcl_value}")
                # If we overwrote a default variable, remove it from defaults list
                if hasattr(interp, '_configkit_default_vars') and name in interp._configkit_default_vars:
                    interp._configkit_default_vars.discard(name)
            else:
                # Array variable with keys joined by commas
                array_indices = ','.join(parent_keys)
                interp.eval(f"set {safe_name}({array_indices}) {tcl_value}")
                # If we overwrote a default variable, remove it from defaults list
                if hasattr(interp, '_configkit_default_vars') and name in interp._configkit_default_vars:
                    interp._configkit_default_vars.discard(name)

    for key, value in data.items():
        _set_tcl_var(key, value)

    # Second pass: resolve variable references (e.g., $a, $env/config)
    def _resolve_variable_references():
        all_vars = interp.eval("info vars").split()
        vars_to_resolve = []
        
        for var in all_vars:
            if var.startswith("__configkit_types__"):
                continue
                
            # Skip default Tcl variables
            if hasattr(interp, '_configkit_default_vars') and var in interp._configkit_default_vars:
                continue
                
            try:
                # Check if it's an array
                is_array = interp.eval(f"array exists {var}") == "1"
                if is_array:
                    # Handle array variables
                    indices = interp.eval(f"array names {var}").split()
                    for idx in indices:
                        try:
                            current_value = interp.eval(f"set {var}({idx})")
                            if '$' in current_value:
                                # Try to resolve variable references
                                resolved_value = interp.eval(f"subst {{{current_value}}}")
                                if resolved_value != current_value:
                                    interp.eval(f"set {var}({idx}) {{{resolved_value}}}")
                        except:
                            continue
                else:
                    # Handle simple variables
                    current_value = interp.eval(f"set {var}")
                    if '$' in current_value:
                        # Try to resolve variable references
                        try:
                            resolved_value = interp.eval(f"subst {{{current_value}}}")
                            if resolved_value != current_value:
                                interp.eval(f"set {var} {{{resolved_value}}}")
                        except:
                            # If substitution fails, keep original value
                            pass
            except:
                continue
    
    _resolve_variable_references()
    return interp


def _write_tcl_vars_to_file(interp: Tcl, file) -> None:
    """Write all user-defined variables from a Tcl interpreter to a file."""
    # Get all global variables
    all_vars = set(interp.eval("info vars").split())
    
    # Get default Tcl variables to filter out
    # Use the default vars recorded when the interpreter was created
    if hasattr(interp, '_configkit_default_vars'):
        default_vars = interp._configkit_default_vars
    else:
        # Fallback: create a fresh interpreter to get defaults
        # This handles cases where the interpreter was created outside our create_tcl_interp()
        fresh_interp = Tcl()
        default_vars = set(fresh_interp.eval("info vars").split())
    
    # Only process variables that are not default Tcl variables
    # Keep __configkit_types__ as it's our special variable
    user_vars = all_vars - default_vars
    if "__configkit_types__" in all_vars:
        user_vars.add("__configkit_types__")

    # Process user-defined variables
    for var in user_vars:
        # Check if it's an array
        is_array = interp.eval(f"array exists {var}")

        if is_array == "1":
            # Get all array indices
            try:
                indices = interp.eval(f"array names {var}").split()

                for idx in indices:
                    try:
                        value = interp.eval(f"set {var}({idx})")
                        # Properly quote the value to ensure it's valid Tcl
                        if ' ' in value or any(c in value for c in '{}[]$"\\'):
                            file.write(f"set {var}({idx}) {{{value}}}\n")
                        else:
                            file.write(f"set {var}({idx}) {value}\n")
                    except Exception:
                        # Skip indices that can't be accessed
                        continue
            except Exception:
                # Skip arrays that can't be accessed
                continue
        else:
            # Simple variable
            try:
                value = interp.eval(f"set {var}")

                # Properly quote the value to ensure it's valid Tcl
                if ' ' in value or any(c in value for c in '{}[]$"\\'):
                    file.write(f"set {var} {{{value}}}\n")
                else:
                    file.write(f"set {var} {value}\n")
            except Exception:
                # Skip variables that can't be accessed
                continue

    # Export type information
    if "__configkit_types__" in all_vars and interp.eval("array exists __configkit_types__") == "1":
        file.write("\n# Type information for configkit\n")
        file.write("array set __configkit_types__ {}\n")

        try:
            type_indices = interp.eval("array names __configkit_types__").split()

            for idx in type_indices:
                try:
                    type_value = interp.eval(f"set __configkit_types__({idx})")
                    # Properly quote both the index and value
                    if ' ' in idx or any(c in idx for c in '{}[]$"\\'):
                        quoted_idx = f"{{{idx}}}"
                    else:
                        quoted_idx = idx

                    file.write(f"set __configkit_types__({quoted_idx}) {type_value}\n")
                except Exception:
                    continue
        except Exception:
            # If we can't access type information, just skip it
            pass


def tclinterp2tclfile(interp: Tcl, output_file: str) -> None:
    """
    Export all variables and arrays from a Tcl interpreter to a Tcl file.
    Also exports type information for proper conversion back to Python.

    Args:
        interp: Tcl interpreter containing variables
        output_file: Path to the output Tcl file

    Returns:
        None
    """
    # Get all global variables
    all_vars = interp.eval("info vars").split()

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Generated by configkit\n\n")

        # First, check if we have type information
        has_type_info = "__configkit_types__" in all_vars and interp.eval("array exists __configkit_types__") == "1"

        # Process regular variables
        for var in all_vars:
            # Skip special Tcl variables and system variables
            if (var.startswith("tcl_") or var.startswith("auto_") or
                var in ["errorInfo", "errorCode", "env", "argv0", "_tkinter_skip_tk_init"]):
                continue

            # Skip our internal type information array (we'll handle it separately)
            if var == "__configkit_types__":
                continue

            # Check if it's an array
            is_array = interp.eval(f"array exists {var}")

            if is_array == "1":
                # Get all array indices
                try:
                    indices = interp.eval(f"array names {var}").split()

                    for idx in indices:
                        try:
                            value = interp.eval(f"set {var}({idx})")
                            # Properly quote the value to ensure it's valid Tcl
                            if ' ' in value or any(c in value for c in '{}[]$"\\'):
                                f.write(f"set {var}({idx}) {{{value}}}\n")
                            else:
                                f.write(f"set {var}({idx}) {value}\n")
                        except Exception:
                            # Skip indices that can't be accessed
                            continue
                except Exception:
                    # Skip arrays that can't be accessed
                    continue
            else:
                # Simple variable
                try:
                    value = interp.eval(f"set {var}")
                    # Properly quote the value to ensure it's valid Tcl
                    if ' ' in value or any(c in value for c in '{}[]$"\\'):
                        f.write(f"set {var} {{{value}}}\n")
                    else:
                        f.write(f"set {var} {value}\n")
                except Exception:
                    # Skip variables that can't be accessed
                    continue

        # Now export type information if available
        if has_type_info:
            f.write("\n# Type information for configkit\n")
            f.write("array set __configkit_types__ {}\n")

            try:
                type_indices = interp.eval("array names __configkit_types__").split()

                for idx in type_indices:
                    try:
                        type_value = interp.eval(f"set __configkit_types__({idx})")
                        # Properly quote both the index and value
                        if ' ' in idx or any(c in idx for c in '{}[]$"\\'):
                            quoted_idx = f"{{{idx}}}"
                        else:
                            quoted_idx = idx

                        f.write(f"set __configkit_types__({quoted_idx}) {type_value}\n")
                    except Exception:
                        continue
            except Exception:
                # If we can't access type information, just skip it
                pass


def tclfiles2tclinterp(*tcl_files: str, interp: Optional[Tcl] = None) -> Tcl:
    """
    Load multiple Tcl files into a Tcl interpreter.

    Args:
        *tcl_files: One or more paths to Tcl files
        interp: Optional Tcl interpreter to use. If None, a new one will be created.

    Returns:
        Tcl interpreter with loaded variables

    Raises:
        FileNotFoundError: If any of the Tcl files doesn't exist
    """
    if interp is None:
        interp = create_tcl_interp()

    for tcl_file in tcl_files:
        if not os.path.exists(tcl_file):
            raise FileNotFoundError(f"Tcl file not found: {tcl_file}")

        # Use source command to load the file
        interp.eval(f"source {{{tcl_file}}}")

    return interp


def tclinterp2dict(interp: Tcl, mode: str = "auto") -> Dict:
    """
    Convert all variables and arrays from a Tcl interpreter to a Python dictionary.
    Uses type information if available to correctly convert values.

    Args:
        interp: Tcl interpreter containing variables
        mode: Conversion mode for space-separated values without type information:
              - "auto": Use type information if available, otherwise make best guess
              - "str": Always treat space-separated values as strings
              - "list": Always convert space-separated values to lists

    Returns:
        Dictionary representation of Tcl variables
    """
    result = {}

    # Get all global variables
    all_vars = interp.eval("info vars").split()

    # Check if we have type information
    has_type_info = "__configkit_types__" in all_vars and interp.eval("array exists __configkit_types__") == "1"

    # Function to get the type of a variable if available
    def get_var_type(var_name: str, idx: str = None) -> str:
        if not has_type_info:
            return "unknown"

        type_key = var_name
        if idx is not None:
            type_key = f"{var_name}({idx})"

        try:
            return interp.eval(f"set __configkit_types__({type_key})")
        except Exception:
            return "unknown"

    # Function to convert a Tcl value to Python based on type information and mode
    def convert_value(value: str, var_type: str, var_name: str = "") -> Any:
        # If we have explicit type information, use it
        if var_type != "unknown":
            if var_type == "list":
                # It's a list, split by spaces and convert each item
                if value.startswith("[list ") and value.endswith("]"):
                    # Already in list format
                    return value_format_tcl2py(value)
                else:
                    # For all other cases, use splitlist directly on the value
                    # This handles both braced lists like "{a} {b}" and simple lists like "a b"
                    items = interp.splitlist(value)
                    return [value_format_tcl2py(item) for item in items]
            elif var_type == "bool":
                return value == "1" or value.lower() == "true"
            elif var_type == "none":
                return None
            elif var_type == "number":
                try:
                    if '.' in value:
                        return float(value)
                    else:
                        return int(value)
                except ValueError:
                    return value
            else:  # string or other types
                return value

        # No explicit type information, use mode to determine behavior
        if mode == "str":
            # Always treat as string
            return value
        elif mode == "list":
            # Always convert space-separated values to lists
            if " " in value and not (value.startswith("{") and value.endswith("}")):
                items = interp.splitlist(value)
                return [value_format_tcl2py(item) for item in items]
            else:
                return value_format_tcl2py(value)
        else:  # mode == "auto" or any other value
            # Try to make a best guess
            # 1. If it's already in Tcl list format, convert it
            if value.startswith("[list ") and value.endswith("]"):
                return value_format_tcl2py(value)

            # 2. If it's a braced string, keep it as a string
            if value.startswith("{") and value.endswith("}"):
                return value[1:-1]  # Remove braces

            # 3. If it doesn't contain spaces, convert normally
            if " " not in value:
                return value_format_tcl2py(value)

            # 4. Check if all items are numbers
            items = value.split()
            all_numbers = True
            for item in items:
                try:
                    float(item)
                except ValueError:
                    all_numbers = False
                    break

            if all_numbers and len(items) > 1:
                # Convert to a list of numbers
                return [float(item) if '.' in item else int(item) for item in items]

            # 5. Check if variable name suggests it's a list
            list_hint_names = ["list", "array", "items", "elements", "values"]
            if var_name and any(hint in var_name.lower() for hint in list_hint_names) and len(items) > 1:
                return items

            # 6. Default to string for safety
            return value

    for var in all_vars:
        # Skip system variables using smart filtering
        if var == "__configkit_types__":
            continue
            
        # Use smart filtering if available
        if hasattr(interp, '_configkit_default_vars'):
            if var in interp._configkit_default_vars:
                continue
        else:
            # Fallback to traditional filtering when smart filtering unavailable
            if (var.startswith("tcl_") or var.startswith("auto_") or
                var in ["errorInfo", "errorCode", "argv0", "_tkinter_skip_tk_init"]):
                continue

        # Check if it's an array
        is_array = interp.eval(f"array exists {var}")

        if is_array == "1":
            # Get all array indices
            try:
                indices = interp.eval(f"array names {var}").split()
                var_dict = {}

                for idx in indices:
                    try:
                        # Get the value
                        value = interp.eval(f"set {var}({idx})")

                        # Get the type if available
                        var_type = get_var_type(var, idx)

                        # Convert to Python value based on type and mode
                        py_value = convert_value(value, var_type, f"{var}({idx})")

                        # Handle nested array indices (comma-separated)
                        if ',' in idx:
                            keys = idx.split(',')
                            current = var_dict

                            # Navigate to the nested dictionary
                            for i, key in enumerate(keys):
                                if i == len(keys) - 1:
                                    # Last key, set the value
                                    current[key] = py_value
                                else:
                                    # Create nested dict if needed
                                    if key not in current or not isinstance(current[key], dict):
                                        current[key] = {}
                                    current = current[key]
                        else:
                            var_dict[idx] = py_value
                    except Exception:
                        # Skip indices that can't be accessed
                        continue

                if var_dict:  # Only add if we have values
                    result[var] = var_dict
            except Exception:
                # Skip arrays that can't be accessed
                continue
        else:
            # Simple variable
            try:
                value = interp.eval(f"set {var}")
                var_type = get_var_type(var)
                result[var] = convert_value(value, var_type, var)
            except Exception:
                # Skip variables that can't be accessed
                continue

    return result 
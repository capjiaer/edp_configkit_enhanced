#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
configkit - A library for configuration transformation between Python and Tcl
configkit - Python 和 Tcl 之间的配置转换库

This library provides functions for converting between Python dictionaries, YAML files,
and Tcl files/interpreters. It handles type conversion, nested structures, and maintains
source information when appropriate.

这个库提供了在 Python 字典、YAML 文件和 Tcl 文件/解释器之间进行转换的功能。
它处理类型转换、嵌套结构，并在适当的情况下维护源信息。

Main functions (主要功能):

- Dictionary operations (字典操作):
  - merge_dict: Merge two dictionaries with nested structure support
                合并两个字典，支持嵌套结构
  - files2dict: Convert mixed YAML and Tcl files to a Python dictionary
                将混合的 YAML 和 Tcl 文件转换为 Python 字典

- Python <-> Tcl conversion (Python <-> Tcl 转换):
  - value_format_py2tcl: Convert a Python value to Tcl format
                         将 Python 值转换为 Tcl 格式
  - value_format_tcl2py: Convert a Tcl value to Python format
                         将 Tcl 值转换为 Python 格式
  - dict2tclinterp: Convert a Python dictionary to a Tcl interpreter
                    将 Python 字典转换为 Tcl 解释器
  - tclinterp2dict: Convert a Tcl interpreter to a Python dictionary
                    将 Tcl 解释器转换为 Python 字典

- File operations (文件操作):
  - yamlfiles2dict: Load one or more YAML files into a Python dictionary
                    将一个或多个 YAML 文件加载到 Python 字典中
  - tclinterp2tclfile: Write a Tcl interpreter to a Tcl file
                       将 Tcl 解释器写入 Tcl 文件
  - tclfiles2tclinterp: Load one or more Tcl files into a Tcl interpreter
                        将一个或多个 Tcl 文件加载到 Tcl 解释器中
  - tclfiles2yamlfile: Convert one or more Tcl files to a YAML file
                       将一个或多个 Tcl 文件转换为 YAML 文件
  - yamlfiles2tclfile: Convert one or more YAML files to a Tcl file
                       将一个或多个 YAML 文件转换为 Tcl 文件
  - files2tclfile: Convert mixed YAML and Tcl files to a Tcl file
                   将混合的 YAML 和 Tcl 文件转换为 Tcl 文件
  - files2yamlfile: Convert mixed YAML and Tcl files to a YAML file
                    将混合的 YAML 和 Tcl 文件转换为 YAML 文件
"""

__version__ = '0.2.0'

# Import from core modules
from .core import (
    # Dictionary operations (字典操作)
    merge_dict,      # Merge two dictionaries with nested structure support (合并两个字典，支持嵌套结构)
    yamlfiles2dict,  # Load one or more YAML files into a Python dictionary (将一个或多个YAML文件加载到Python字典中)

    # Value format conversion (值格式转换)
    value_format_py2tcl,  # Convert a Python value to Tcl format (将Python值转换为Tcl格式)
    value_format_tcl2py,  # Convert a Tcl value to Python format (将Tcl值转换为Python格式)

    # Python <-> Tcl conversion (Python <-> Tcl 转换)
    dict2tclinterp,      # Convert a Python dictionary to a Tcl interpreter (将Python字典转换为Tcl解释器)
    tclinterp2dict,      # Convert a Tcl interpreter to a Python dictionary (将Tcl解释器转换为Python字典)

    # File operations (文件操作)
    tclinterp2tclfile,   # Write a Tcl interpreter to a Tcl file (将Tcl解释器写入Tcl文件)
    tclfiles2tclinterp,  # Load one or more Tcl files into a Tcl interpreter (将一个或多个Tcl文件加载到Tcl解释器中)
)

# Import from API modules
from .api import (
    files2dict,      # Convert mixed YAML and Tcl files to a Python dictionary (将混合的YAML和Tcl文件转换为Python字典)
    tclfiles2yamlfile,   # Convert one or more Tcl files to a YAML file (将一个或多个Tcl文件转换为YAML文件)
    yamlfiles2tclfile,   # Convert one or more YAML files to a Tcl file with source annotations (将一个或多个YAML文件转换为带源注释的Tcl文件)
    files2tclfile,       # Convert mixed YAML and Tcl files to a Tcl file with source annotations (将混合的YAML和Tcl文件转换为带源注释的Tcl文件)
    files2yamlfile       # Convert mixed YAML and Tcl files to a YAML file (将混合的YAML和Tcl文件转换为YAML文件)
)

__all__ = [
    # Dictionary operations (字典操作)
    'merge_dict',      # Merge two dictionaries with nested structure support (合并两个字典，支持嵌套结构)
    'yamlfiles2dict',  # Load one or more YAML files into a Python dictionary (将一个或多个YAML文件加载到Python字典中)
    'files2dict',      # Convert mixed YAML and Tcl files to a Python dictionary (将混合的YAML和Tcl文件转换为Python字典)

    # Value format conversion (值格式转换)
    'value_format_py2tcl',  # Convert a Python value to Tcl format (将Python值转换为Tcl格式)
    'value_format_tcl2py',  # Convert a Tcl value to Python format (将Tcl值转换为Python格式)

    # Python <-> Tcl conversion (Python <-> Tcl 转换)
    'dict2tclinterp',      # Convert a Python dictionary to a Tcl interpreter (将Python字典转换为Tcl解释器)
    'tclinterp2dict',      # Convert a Tcl interpreter to a Python dictionary (将Tcl解释器转换为Python字典)

    # File operations (文件操作)
    'tclinterp2tclfile',   # Write a Tcl interpreter to a Tcl file (将Tcl解释器写入Tcl文件)
    'tclfiles2tclinterp',  # Load one or more Tcl files into a Tcl interpreter (将一个或多个Tcl文件加载到Tcl解释器中)
    'tclfiles2yamlfile',   # Convert one or more Tcl files to a YAML file (将一个或多个Tcl文件转换为YAML文件)
    'yamlfiles2tclfile',   # Convert one or more YAML files to a Tcl file with source annotations (将一个或多个YAML文件转换为带源注释的Tcl文件)
    'files2tclfile',       # Convert mixed YAML and Tcl files to a Tcl file with source annotations (将混合的YAML和Tcl文件转换为带源注释的Tcl文件)
    'files2yamlfile'       # Convert mixed YAML and Tcl files to a YAML file (将混合的YAML和Tcl文件转换为YAML文件)
] 
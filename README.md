# EDP ConfigKit Enhanced

[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.2.0-orange.svg)](https://github.com/yourusername/edp_configkit_enhanced)

> Enhanced ConfigKit - A powerful library for configuration transformation between Python and Tcl with advanced variable resolution capabilities.

## 🚀 What's New in Enhanced Version

This is a **fully refactored and enhanced version** of the original ConfigKit library, featuring:

### ✨ New Features
- **🔀 Variable Resolution**: YAML files can now contain variables (e.g., `$var`) that get resolved automatically
- **🔗 Cross-file Variables**: Variables defined in Tcl files can be referenced in YAML files and vice versa
- **🛡️ Smart Filtering**: Intelligent handling of Tcl system variables to avoid conflicts
- **🏗️ Modular Architecture**: Clean separation of concerns with core/api module structure

### 🔄 Improvements
- **100% Backward Compatibility**: All existing APIs work exactly as before
- **Enhanced Error Handling**: Better error messages and conflict resolution
- **Performance Optimizations**: Modular loading and improved memory management
- **Better Type Support**: Enhanced type hints and documentation

## 📦 Installation

### From Source
```bash
git clone https://github.com/yourusername/edp_configkit_enhanced.git
cd edp_configkit_enhanced
pip install -e .
```

### Development Installation
```bash
pip install -e ".[dev]"
```

## 🎯 Quick Start

### Basic Usage (Compatible with Original ConfigKit)
```python
from configkit import files2dict, yamlfiles2dict

# Load YAML files
config = yamlfiles2dict("config.yaml")

# Load mixed YAML and Tcl files
mixed_config = files2dict("base.tcl", "app.yaml")
```

### New Variable Resolution Features
```python
from configkit import yamlfiles2dict, files2dict
from configkit.core.tcl_interpreter import create_tcl_interp

# Create an interpreter for variable resolution
interp = create_tcl_interp()

# YAML with variables
config = yamlfiles2dict("config.yaml", variable_interp=interp)
# Now $variable_name in YAML will be resolved to actual values

# Cross-file variable resolution
config = files2dict("base.tcl", "app.yaml", variable_interp=interp)
# Variables from base.tcl can be used in app.yaml
```

## 📚 Documentation

### Core Functions

#### Dictionary Operations
- `merge_dict(dict1, dict2)` - Merge dictionaries with nested structure support
- `yamlfiles2dict(*yaml_files, variable_interp=None)` - Load YAML files with optional variable resolution
- `files2dict(*input_files, variable_interp=None)` - Convert mixed YAML/Tcl files to dictionary

#### Value Conversion
- `value_format_py2tcl(value)` - Convert Python value to Tcl format
- `value_format_tcl2py(value, mode="auto")` - Convert Tcl value to Python format

#### Python ↔ Tcl Conversion
- `dict2tclinterp(dict_data, interp)` - Convert Python dictionary to Tcl interpreter
- `tclinterp2dict(interp, mode="auto")` - Convert Tcl interpreter to Python dictionary

#### File Operations
- `yamlfiles2tclfile(*yaml_files, output_file)` - Convert YAML files to Tcl file
- `tclfiles2yamlfile(*tcl_files, output_file)` - Convert Tcl files to YAML file
- `files2tclfile(*input_files, output_file)` - Convert mixed files to Tcl file
- `files2yamlfile(*input_files, output_file)` - Convert mixed files to YAML file

### Advanced Features

#### Smart Tcl Interpreter Creation
```python
from configkit.core.tcl_interpreter import create_tcl_interp

# Creates a Tcl interpreter with smart filtering of system variables
interp = create_tcl_interp()
```

#### Variable Resolution Examples

**Basic Variable Resolution:**
```yaml
# config.yaml
base_url: "https://api.example.com"
version: "v1"
endpoint: "$base_url/$version"
```

```python
interp = create_tcl_interp()
config = yamlfiles2dict("config.yaml", variable_interp=interp)
print(config['endpoint'])  # Output: https://api.example.com/v1
```

**Cross-file Variable Resolution:**
```tcl
# base.tcl
set environment "production"
set host "192.168.1.100"
```

```yaml
# app.yaml
database:
  host: $host
  port: 5432
log_path: "/var/log/$environment/app.log"
```

```python
interp = create_tcl_interp()
config = files2dict("base.tcl", "app.yaml", variable_interp=interp)
print(config['database']['host'])  # Output: 192.168.1.100
print(config['log_path'])          # Output: /var/log/production/app.log
```

## 🏗️ Architecture

### Project Structure
```
edp_configkit_enhanced/
├── configkit/
│   ├── __init__.py          # Main API exports
│   ├── core/                # Core functionality
│   │   ├── dict_operations.py    # Dictionary operations
│   │   ├── value_converter.py    # Value conversion
│   │   ├── tcl_interpreter.py    # Tcl interpreter handling
│   │   └── __init__.py
│   └── api/                 # High-level API
│       ├── file_converters.py    # File conversion functions
│       └── __init__.py
├── examples/                # Usage examples
├── tests/                   # Unit tests
├── docs/                    # Documentation
├── setup.py                 # Package setup
├── requirements.txt         # Dependencies
└── README.md               # This file
```

### Module Responsibilities
- **`core/dict_operations.py`**: Dictionary merging and YAML processing
- **`core/value_converter.py`**: Python ↔ Tcl value conversion
- **`core/tcl_interpreter.py`**: Tcl interpreter management and variable resolution
- **`api/file_converters.py`**: High-level file conversion APIs

## 🔄 Migration from Original ConfigKit

### No Changes Required
All existing code will work without modification:
```python
# This code works exactly the same
from configkit import files2dict, yamlfiles2dict
config = files2dict("base.tcl", "app.yaml")
```

### Optional Enhancements
To use new features, simply add the variable resolution parameter:
```python
from configkit.core.tcl_interpreter import create_tcl_interp
interp = create_tcl_interp()
config = files2dict("base.tcl", "app.yaml", variable_interp=interp)
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=configkit

# Run specific test file
python -m pytest tests/test_variable_resolution.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📋 Version History

### v0.2.0 (Enhanced Version)
- ✨ Added variable resolution for YAML files
- 🔗 Cross-file variable resolution support
- 🛡️ Smart filtering of Tcl system variables
- 🏗️ Modular architecture refactoring
- 📈 Performance improvements
- 🔄 100% backward compatibility maintained

### v0.1.0 (Original Version)
- Basic YAML ↔ Tcl conversion
- Dictionary operations
- File format transformations

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

If you encounter any issues or have questions:
- Open an issue on [GitHub Issues](https://github.com/yourusername/edp_configkit_enhanced/issues)
- Check the [documentation](docs/)
- Review the [examples](examples/)

## 🌟 Key Features Summary

| Feature | Original | Enhanced | Description |
|---------|----------|----------|-------------|
| **YAML → Dict** | ✅ | ✅ | Basic YAML loading |
| **Tcl → Dict** | ✅ | ✅ | Basic Tcl conversion |
| **Mixed Files** | ✅ | ✅ | YAML + Tcl processing |
| **Variable Resolution** | ❌ | ✅ | `$var` expansion in YAML |
| **Cross-file Variables** | ❌ | ✅ | Variables across file types |
| **Smart Filtering** | ❌ | ✅ | Intelligent system variable handling |
| **Modular Architecture** | ❌ | ✅ | Clean code organization |
| **Backward Compatibility** | - | ✅ | 100% compatible with v0.1.0 |

---

**Built with ❤️ for the EDA community** 🚀 
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2024-01-XX

### Added
- **Variable Resolution**: YAML files can now contain variables (e.g., `$var`) that get resolved automatically
- **Cross-file Variables**: Variables defined in Tcl files can be referenced in YAML files and vice versa
- **Smart Filtering**: Intelligent handling of Tcl system variables to avoid conflicts
- **Modular Architecture**: Clean separation of concerns with core/api module structure
- **Enhanced create_tcl_interp()**: Smart interpreter creation with default variable filtering
- **Advanced Examples**: Comprehensive examples for basic and advanced usage
- **Comprehensive Tests**: Unit tests for all functionality including variable resolution

### Changed
- **Refactored Architecture**: Separated single 923-line file into modular components:
  - `core/dict_operations.py` - Dictionary operations and YAML processing
  - `core/value_converter.py` - Python ↔ Tcl value conversion
  - `core/tcl_interpreter.py` - Tcl interpreter management and variable resolution
  - `api/file_converters.py` - High-level file conversion APIs
- **Enhanced yamlfiles2dict()**: Added optional `variable_interp` parameter for variable resolution
- **Enhanced files2dict()**: Added optional `variable_interp` parameter for cross-file variable resolution
- **Improved Error Handling**: Better error messages and conflict resolution
- **Performance Optimizations**: Modular loading and improved memory management

### Fixed
- **Tcl List Processing**: Fixed incorrect list parsing that caused data loss
- **System Variable Conflicts**: Resolved conflicts with built-in Tcl variables like `env`
- **Variable Resolution Edge Cases**: Proper handling of undefined variables and recursive references

### Compatibility
- **100% Backward Compatibility**: All existing APIs work exactly as before
- **No Breaking Changes**: Existing code requires no modifications
- **Optional Enhancements**: New features are opt-in via additional parameters

## [0.1.0] - 2023-XX-XX

### Added
- Initial release with basic functionality
- YAML ↔ Tcl file conversion
- Dictionary operations and merging
- Mixed file format support
- Basic value type conversion
- File I/O operations

---

## Migration Guide

### From v0.1.0 to v0.2.0

**No changes required for existing code** - all APIs remain compatible.

**To use new features:**

```python
# Before (still works)
from configkit import files2dict
config = files2dict("base.tcl", "app.yaml")

# After (with new variable resolution)
from configkit import files2dict
from configkit.core.tcl_interpreter import create_tcl_interp
interp = create_tcl_interp()
config = files2dict("base.tcl", "app.yaml", variable_interp=interp)
```

### New Import Options

```python
# Basic import (same as before)
from configkit import files2dict, yamlfiles2dict

# Advanced features
from configkit.core.tcl_interpreter import create_tcl_interp

# Modular imports
import configkit.core as core
import configkit.api as api
``` 
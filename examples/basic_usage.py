#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Basic usage examples for edp_configkit_enhanced

This file demonstrates the basic functionality of the ConfigKit library.
"""

import os
import sys
import tempfile
import yaml

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configkit import (
    files2dict, yamlfiles2dict, 
    yamlfiles2tclfile, tclfiles2yamlfile,
    files2tclfile, files2yamlfile
)

def example_basic_yaml_loading():
    """Basic YAML file loading example"""
    print("=== Basic YAML Loading ===")
    
    # Create a temporary YAML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump({
            'app_name': 'MyApplication',
            'version': '1.0.0',
            'database': {
                'host': 'localhost',
                'port': 5432,
                'name': 'mydb'
            },
            'features': ['auth', 'logging', 'metrics']
        }, f)
        yaml_file = f.name
    
    try:
        # Load the YAML file
        config = yamlfiles2dict(yaml_file)
        print(f"Loaded config: {config}")
        
        # Access nested values
        print(f"App name: {config['app_name']}")
        print(f"Database host: {config['database']['host']}")
        print(f"Features: {config['features']}")
        
    finally:
        os.unlink(yaml_file)

def example_mixed_file_loading():
    """Mixed YAML and Tcl file loading example"""
    print("\n=== Mixed File Loading ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a Tcl file
        tcl_file = os.path.join(temp_dir, 'config.tcl')
        with open(tcl_file, 'w') as f:
            f.write("""
set environment "production"
set debug_mode 0
set max_connections 100
""")
        
        # Create a YAML file
        yaml_file = os.path.join(temp_dir, 'app.yaml')
        with open(yaml_file, 'w') as f:
            yaml.dump({
                'app_name': 'WebService',
                'api_version': 'v2',
                'endpoints': {
                    'health': '/health',
                    'metrics': '/metrics'
                }
            }, f)
        
        # Load both files
        config = files2dict(tcl_file, yaml_file)
        print(f"Mixed config: {config}")
        
        # Show values from both files
        print(f"Environment (from Tcl): {config.get('environment')}")
        print(f"App name (from YAML): {config.get('app_name')}")
        print(f"Debug mode (from Tcl): {config.get('debug_mode')}")
        print(f"Endpoints (from YAML): {config.get('endpoints')}")

def example_file_format_conversion():
    """File format conversion examples"""
    print("\n=== File Format Conversion ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create source YAML file
        source_yaml = os.path.join(temp_dir, 'source.yaml')
        with open(source_yaml, 'w') as f:
            yaml.dump({
                'server': {
                    'host': 'localhost',
                    'port': 8080
                },
                'database': {
                    'url': 'postgresql://localhost:5432/mydb',
                    'pool_size': 10
                },
                'logging': {
                    'level': 'INFO',
                    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                }
            }, f)
        
        # Convert YAML to Tcl
        output_tcl = os.path.join(temp_dir, 'output.tcl')
        yamlfiles2tclfile(source_yaml, output_file=output_tcl)
        
        print(f"Converted YAML to Tcl:")
        with open(output_tcl, 'r') as f:
            print(f.read())
        
        # Convert Tcl back to YAML
        output_yaml = os.path.join(temp_dir, 'output.yaml')
        tclfiles2yamlfile(output_tcl, output_file=output_yaml)
        
        print(f"Converted Tcl back to YAML:")
        with open(output_yaml, 'r') as f:
            print(f.read())

def example_multiple_files():
    """Multiple file processing example"""
    print("\n=== Multiple Files Processing ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create multiple configuration files
        files = []
        
        # Base configuration
        base_yaml = os.path.join(temp_dir, 'base.yaml')
        with open(base_yaml, 'w') as f:
            yaml.dump({
                'app_name': 'MultiConfig',
                'version': '1.0.0'
            }, f)
        files.append(base_yaml)
        
        # Environment configuration
        env_tcl = os.path.join(temp_dir, 'env.tcl')
        with open(env_tcl, 'w') as f:
            f.write("""
set environment "staging"
set debug_enabled 1
""")
        files.append(env_tcl)
        
        # Service configuration
        service_yaml = os.path.join(temp_dir, 'service.yaml')
        with open(service_yaml, 'w') as f:
            yaml.dump({
                'services': {
                    'web': {'port': 8080},
                    'api': {'port': 8081},
                    'db': {'port': 5432}
                }
            }, f)
        files.append(service_yaml)
        
        # Load all files
        config = files2dict(*files)
        print(f"Combined config from {len(files)} files: {config}")
        
        # Convert all to single Tcl file
        output_tcl = os.path.join(temp_dir, 'combined.tcl')
        files2tclfile(*files, output_file=output_tcl)
        
        print(f"\nCombined Tcl file content:")
        with open(output_tcl, 'r') as f:
            print(f.read())

if __name__ == '__main__':
    print("🚀 ConfigKit Enhanced - Basic Usage Examples")
    print("=" * 60)
    
    example_basic_yaml_loading()
    example_mixed_file_loading()
    example_file_format_conversion()
    example_multiple_files()
    
    print("\n✅ All basic examples completed successfully!") 
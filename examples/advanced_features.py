#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Advanced features examples for edp_configkit_enhanced

This file demonstrates the advanced functionality including variable resolution
and cross-file variable references.
"""

import os
import sys
import tempfile
import yaml

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configkit import files2dict, yamlfiles2dict
from configkit.core.tcl_interpreter import create_tcl_interp

def example_variable_resolution():
    """Variable resolution within YAML files"""
    print("=== Variable Resolution in YAML ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create YAML with variables
        yaml_file = os.path.join(temp_dir, 'config.yaml')
        with open(yaml_file, 'w') as f:
            yaml.dump({
                'base_url': 'https://api.example.com',
                'api_version': 'v2',
                'endpoints': {
                    'users': '$base_url/$api_version/users',
                    'posts': '$base_url/$api_version/posts',
                    'health': '$base_url/$api_version/health'
                },
                'full_health_url': '$endpoints.health'
            }, f)
        
        # Load without variable resolution
        config_no_vars = yamlfiles2dict(yaml_file)
        print("Without variable resolution:")
        print(f"  Users endpoint: {config_no_vars['endpoints']['users']}")
        print(f"  Posts endpoint: {config_no_vars['endpoints']['posts']}")
        
        # Load with variable resolution
        interp = create_tcl_interp()
        config_with_vars = yamlfiles2dict(yaml_file, variable_interp=interp)
        print("\nWith variable resolution:")
        print(f"  Users endpoint: {config_with_vars['endpoints']['users']}")
        print(f"  Posts endpoint: {config_with_vars['endpoints']['posts']}")
        print(f"  Health endpoint: {config_with_vars['endpoints']['health']}")

def example_cross_file_variables():
    """Cross-file variable resolution"""
    print("\n=== Cross-file Variable Resolution ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create Tcl file with base configuration
        tcl_file = os.path.join(temp_dir, 'base.tcl')
        with open(tcl_file, 'w') as f:
            f.write("""
set environment "production"
set app_name "MyWebApp"
set host "192.168.1.100"
set port 8080
set db_host "db.example.com"
set db_port 5432
""")
        
        # Create YAML file that uses Tcl variables
        yaml_file = os.path.join(temp_dir, 'app.yaml')
        with open(yaml_file, 'w') as f:
            yaml.dump({
                'application': {
                    'name': '$app_name',
                    'environment': '$environment',
                    'url': 'https://$host:$port'
                },
                'database': {
                    'host': '$db_host',
                    'port': '$db_port',
                    'url': 'postgresql://$db_host:$db_port/mydb'
                },
                'logging': {
                    'level': 'INFO',
                    'file': '/var/log/$environment/$app_name.log'
                }
            }, f)
        
        # Load without variable resolution
        config_no_vars = files2dict(tcl_file, yaml_file)
        print("Without variable resolution:")
        print(f"  App URL: {config_no_vars['application']['url']}")
        print(f"  DB URL: {config_no_vars['database']['url']}")
        print(f"  Log file: {config_no_vars['logging']['file']}")
        
        # Load with variable resolution
        interp = create_tcl_interp()
        config_with_vars = files2dict(tcl_file, yaml_file, variable_interp=interp)
        print("\nWith variable resolution:")
        print(f"  App URL: {config_with_vars['application']['url']}")
        print(f"  DB URL: {config_with_vars['database']['url']}")
        print(f"  Log file: {config_with_vars['logging']['file']}")

def example_complex_variable_chains():
    """Complex variable chains and nested references"""
    print("\n=== Complex Variable Chains ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create multiple files with interdependent variables
        
        # Environment configuration
        env_tcl = os.path.join(temp_dir, 'env.tcl')
        with open(env_tcl, 'w') as f:
            f.write("""
set deploy_env "staging"
set region "us-west-2"
set cluster_name "web-cluster"
""")
        
        # Service configuration
        service_yaml = os.path.join(temp_dir, 'service.yaml')
        with open(service_yaml, 'w') as f:
            yaml.dump({
                'service_prefix': '$cluster_name-$deploy_env',
                'dns_suffix': '$region.amazonaws.com'
            }, f)
        
        # Application configuration
        app_yaml = os.path.join(temp_dir, 'app.yaml')
        with open(app_yaml, 'w') as f:
            yaml.dump({
                'services': {
                    'web': {
                        'name': '$service_prefix-web',
                        'url': 'https://$service_prefix-web.$dns_suffix'
                    },
                    'api': {
                        'name': '$service_prefix-api',
                        'url': 'https://$service_prefix-api.$dns_suffix'
                    },
                    'worker': {
                        'name': '$service_prefix-worker',
                        'url': 'https://$service_prefix-worker.$dns_suffix'
                    }
                },
                'load_balancer': {
                    'name': '$service_prefix-lb',
                    'targets': [
                        '$services.web.url',
                        '$services.api.url'
                    ]
                }
            }, f)
        
        # Process with variable resolution
        interp = create_tcl_interp()
        config = files2dict(env_tcl, service_yaml, app_yaml, variable_interp=interp)
        
        print("Complex variable resolution results:")
        print(f"  Service prefix: {config['service_prefix']}")
        print(f"  DNS suffix: {config['dns_suffix']}")
        print(f"  Web service URL: {config['services']['web']['url']}")
        print(f"  API service URL: {config['services']['api']['url']}")
        print(f"  Worker service URL: {config['services']['worker']['url']}")
        print(f"  Load balancer name: {config['load_balancer']['name']}")

def example_conditional_configuration():
    """Conditional configuration based on environment"""
    print("\n=== Conditional Configuration ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create environment-specific configurations
        for env in ['development', 'staging', 'production']:
            env_tcl = os.path.join(temp_dir, f'{env}.tcl')
            if env == 'development':
                content = """
set environment "development"
set debug_mode 1
set log_level "DEBUG"
set db_host "localhost"
set db_pool_size 5
"""
            elif env == 'staging':
                content = """
set environment "staging"
set debug_mode 1
set log_level "INFO"
set db_host "staging-db.example.com"
set db_pool_size 10
"""
            else:  # production
                content = """
set environment "production"
set debug_mode 0
set log_level "WARNING"
set db_host "prod-db.example.com"
set db_pool_size 20
"""
            
            with open(env_tcl, 'w') as f:
                f.write(content)
        
        # Create common application configuration
        app_yaml = os.path.join(temp_dir, 'app.yaml')
        with open(app_yaml, 'w') as f:
            yaml.dump({
                'application': {
                    'name': 'ConfigDemo',
                    'environment': '$environment',
                    'debug': '$debug_mode'
                },
                'logging': {
                    'level': '$log_level',
                    'file': '/var/log/$environment/app.log'
                },
                'database': {
                    'host': '$db_host',
                    'port': 5432,
                    'pool_size': '$db_pool_size'
                }
            }, f)
        
        # Process each environment
        for env in ['development', 'staging', 'production']:
            env_tcl = os.path.join(temp_dir, f'{env}.tcl')
            interp = create_tcl_interp()
            config = files2dict(env_tcl, app_yaml, variable_interp=interp)
            
            print(f"\n{env.upper()} configuration:")
            print(f"  Environment: {config['application']['environment']}")
            print(f"  Debug mode: {config['application']['debug']}")
            print(f"  Log level: {config['logging']['level']}")
            print(f"  DB host: {config['database']['host']}")
            print(f"  DB pool size: {config['database']['pool_size']}")

def example_smart_filtering():
    """Demonstrate smart filtering of system variables"""
    print("\n=== Smart Filtering Demo ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create Tcl file that might conflict with system variables
        tcl_file = os.path.join(temp_dir, 'config.tcl')
        with open(tcl_file, 'w') as f:
            f.write("""
set my_env "custom_environment"
set my_path "/custom/path"
set my_home "/custom/home"
set custom_var "my_value"
""")
        
        # Create YAML that uses these variables
        yaml_file = os.path.join(temp_dir, 'app.yaml')
        with open(yaml_file, 'w') as f:
            yaml.dump({
                'config': {
                    'environment': '$my_env',
                    'path': '$my_path',
                    'home': '$my_home',
                    'custom': '$custom_var'
                }
            }, f)
        
        # Process with smart filtering
        interp = create_tcl_interp()
        config = files2dict(tcl_file, yaml_file, variable_interp=interp)
        
        print("Smart filtering results:")
        print(f"  Custom environment: {config['config']['environment']}")
        print(f"  Custom path: {config['config']['path']}")
        print(f"  Custom home: {config['config']['home']}")
        print(f"  Custom variable: {config['config']['custom']}")
        
        # The system variables (env, tcl_library, etc.) are filtered out
        # and don't appear in the final configuration

if __name__ == '__main__':
    print("🚀 ConfigKit Enhanced - Advanced Features Examples")
    print("=" * 60)
    
    example_variable_resolution()
    example_cross_file_variables()
    example_complex_variable_chains()
    example_conditional_configuration()
    example_smart_filtering()
    
    print("\n✅ All advanced examples completed successfully!") 
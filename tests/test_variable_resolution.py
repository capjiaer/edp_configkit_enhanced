#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Variable resolution tests for edp_configkit_enhanced
"""

import os
import tempfile
import unittest
import yaml
from configkit import files2dict, yamlfiles2dict
from configkit.core.tcl_interpreter import create_tcl_interp

class TestVariableResolution(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_basic_variable_resolution(self):
        """Test basic variable resolution in YAML"""
        yaml_file = os.path.join(self.temp_dir, 'config.yaml')
        test_data = {
            'base_url': 'https://api.example.com',
            'version': 'v1',
            'endpoint': '$base_url/$version'
        }
        
        with open(yaml_file, 'w') as f:
            yaml.dump(test_data, f)
        
        # Test without variable resolution
        result_no_vars = yamlfiles2dict(yaml_file)
        self.assertEqual(result_no_vars['endpoint'], '$base_url/$version')
        
        # Test with variable resolution
        interp = create_tcl_interp()
        result_with_vars = yamlfiles2dict(yaml_file, variable_interp=interp)
        self.assertEqual(result_with_vars['endpoint'], 'https://api.example.com/v1')
        
    def test_nested_variable_resolution(self):
        """Test variable resolution in nested structures"""
        yaml_file = os.path.join(self.temp_dir, 'config.yaml')
        test_data = {
            'host': 'localhost',
            'port': 8080,
            'database': {
                'host': '$host',
                'port': '$port',
                'url': 'postgresql://$host:$port/mydb'
            }
        }
        
        with open(yaml_file, 'w') as f:
            yaml.dump(test_data, f)
        
        interp = create_tcl_interp()
        result = yamlfiles2dict(yaml_file, variable_interp=interp)
        
        self.assertEqual(result['database']['host'], 'localhost')
        self.assertEqual(result['database']['port'], '8080')
        self.assertEqual(result['database']['url'], 'postgresql://localhost:8080/mydb')
        
    def test_cross_file_variable_resolution(self):
        """Test variable resolution across Tcl and YAML files"""
        tcl_file = os.path.join(self.temp_dir, 'base.tcl')
        yaml_file = os.path.join(self.temp_dir, 'app.yaml')
        
        # Create Tcl file with variables
        with open(tcl_file, 'w') as f:
            f.write("""
set environment "production"
set log_level "info"
set host "192.168.1.100"
""")
        
        # Create YAML file that uses Tcl variables
        yaml_data = {
            'app_name': 'WebApp',
            'log_path': '/var/log/$environment/app.log',
            'database': {
                'host': '$host',
                'port': 5432
            },
            'logging': {
                'level': '$log_level'
            }
        }
        
        with open(yaml_file, 'w') as f:
            yaml.dump(yaml_data, f)
        
        # Test without variable resolution
        result_no_vars = files2dict(tcl_file, yaml_file)
        self.assertEqual(result_no_vars['log_path'], '/var/log/$environment/app.log')
        self.assertEqual(result_no_vars['database']['host'], '$host')
        
        # Test with variable resolution
        interp = create_tcl_interp()
        result_with_vars = files2dict(tcl_file, yaml_file, variable_interp=interp)
        self.assertEqual(result_with_vars['log_path'], '/var/log/production/app.log')
        self.assertEqual(result_with_vars['database']['host'], '192.168.1.100')
        self.assertEqual(result_with_vars['logging']['level'], 'info')
        
    def test_complex_variable_chains(self):
        """Test complex variable chains and dependencies"""
        yaml_file = os.path.join(self.temp_dir, 'config.yaml')
        test_data = {
            'app_name': 'MyApp',
            'environment': 'staging',
            'service_prefix': '$app_name-$environment',
            'api_url': 'https://$service_prefix.example.com',
            'health_check': '$api_url/health'
        }
        
        with open(yaml_file, 'w') as f:
            yaml.dump(test_data, f)
        
        interp = create_tcl_interp()
        result = yamlfiles2dict(yaml_file, variable_interp=interp)
        
        self.assertEqual(result['service_prefix'], 'MyApp-staging')
        self.assertEqual(result['api_url'], 'https://MyApp-staging.example.com')
        self.assertEqual(result['health_check'], 'https://MyApp-staging.example.com/health')
        
    def test_variable_resolution_with_lists(self):
        """Test variable resolution in lists"""
        yaml_file = os.path.join(self.temp_dir, 'config.yaml')
        test_data = {
            'base_url': 'https://api.example.com',
            'version': 'v1',
            'endpoints': [
                '$base_url/$version/users',
                '$base_url/$version/posts',
                '$base_url/$version/health'
            ]
        }
        
        with open(yaml_file, 'w') as f:
            yaml.dump(test_data, f)
        
        interp = create_tcl_interp()
        result = yamlfiles2dict(yaml_file, variable_interp=interp)
        
        expected_endpoints = [
            'https://api.example.com/v1/users',
            'https://api.example.com/v1/posts',
            'https://api.example.com/v1/health'
        ]
        
        self.assertEqual(result['endpoints'], expected_endpoints)
        
    def test_multiple_files_variable_resolution(self):
        """Test variable resolution across multiple files"""
        # Create multiple files with interdependent variables
        env_tcl = os.path.join(self.temp_dir, 'env.tcl')
        with open(env_tcl, 'w') as f:
            f.write("""
set deploy_env "staging"
set region "us-west-2"
""")
        
        service_yaml = os.path.join(self.temp_dir, 'service.yaml')
        with open(service_yaml, 'w') as f:
            yaml.dump({
                'service_name': 'web-service',
                'full_name': '$service_name-$deploy_env'
            }, f)
        
        app_yaml = os.path.join(self.temp_dir, 'app.yaml')
        with open(app_yaml, 'w') as f:
            yaml.dump({
                'application': {
                    'name': '$full_name',
                    'region': '$region',
                    'url': 'https://$full_name.$region.amazonaws.com'
                }
            }, f)
        
        interp = create_tcl_interp()
        result = files2dict(env_tcl, service_yaml, app_yaml, variable_interp=interp)
        
        self.assertEqual(result['full_name'], 'web-service-staging')
        self.assertEqual(result['application']['name'], 'web-service-staging')
        self.assertEqual(result['application']['region'], 'us-west-2')
        self.assertEqual(result['application']['url'], 'https://web-service-staging.us-west-2.amazonaws.com')
        
    def test_variable_resolution_with_numbers(self):
        """Test variable resolution with numeric values"""
        yaml_file = os.path.join(self.temp_dir, 'config.yaml')
        test_data = {
            'base_port': 8000,
            'web_port': '$base_port',
            'api_port': 8001,
            'db_port': 5432,
            'connection_string': 'host:$db_port'
        }
        
        with open(yaml_file, 'w') as f:
            yaml.dump(test_data, f)
        
        interp = create_tcl_interp()
        result = yamlfiles2dict(yaml_file, variable_interp=interp)
        
        # Note: Variables resolved by Tcl become strings
        self.assertEqual(result['web_port'], '8000')
        self.assertEqual(result['connection_string'], 'host:5432')
        # Original non-variable values keep their types
        self.assertEqual(result['base_port'], 8000)
        self.assertEqual(result['api_port'], 8001)
        
    def test_missing_variable_handling(self):
        """Test handling of missing variables"""
        yaml_file = os.path.join(self.temp_dir, 'config.yaml')
        test_data = {
            'defined_var': 'value',
            'using_defined': '$defined_var',
            'using_undefined': '$undefined_var'
        }
        
        with open(yaml_file, 'w') as f:
            yaml.dump(test_data, f)
        
        interp = create_tcl_interp()
        result = yamlfiles2dict(yaml_file, variable_interp=interp)
        
        self.assertEqual(result['using_defined'], 'value')
        # Undefined variables remain as-is
        self.assertEqual(result['using_undefined'], '$undefined_var')
        
    def test_smart_filtering(self):
        """Test that system variables are properly filtered"""
        tcl_file = os.path.join(self.temp_dir, 'config.tcl')
        with open(tcl_file, 'w') as f:
            f.write("""
set my_var "my_value"
set another_var "another_value"
""")
        
        yaml_file = os.path.join(self.temp_dir, 'app.yaml')
        with open(yaml_file, 'w') as f:
            yaml.dump({
                'config': {
                    'my_setting': '$my_var',
                    'another_setting': '$another_var'
                }
            }, f)
        
        interp = create_tcl_interp()
        result = files2dict(tcl_file, yaml_file, variable_interp=interp)
        
        # Our variables should be resolved
        self.assertEqual(result['config']['my_setting'], 'my_value')
        self.assertEqual(result['config']['another_setting'], 'another_value')
        
        # System variables should not appear in the result
        # (they are filtered out by the smart filtering mechanism)
        system_vars = ['env', 'tcl_library', 'tcl_version', 'argv', 'argc']
        for var in system_vars:
            self.assertNotIn(var, result)

if __name__ == '__main__':
    unittest.main() 
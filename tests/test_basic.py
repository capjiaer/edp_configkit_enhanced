#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Basic functionality tests for edp_configkit_enhanced
"""

import os
import tempfile
import unittest
import yaml
from configkit import (
    files2dict, yamlfiles2dict, merge_dict,
    dict2tclinterp, tclinterp2dict,
    yamlfiles2tclfile, tclfiles2yamlfile
)
from configkit.core.tcl_interpreter import create_tcl_interp

class TestBasicFunctionality(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_yamlfiles2dict_basic(self):
        """Test basic YAML file loading"""
        yaml_file = os.path.join(self.temp_dir, 'test.yaml')
        test_data = {
            'app_name': 'TestApp',
            'version': '1.0.0',
            'config': {
                'debug': True,
                'port': 8080
            }
        }
        
        with open(yaml_file, 'w') as f:
            yaml.dump(test_data, f)
        
        result = yamlfiles2dict(yaml_file)
        self.assertEqual(result, test_data)
        
    def test_yamlfiles2dict_multiple_files(self):
        """Test loading multiple YAML files"""
        yaml1 = os.path.join(self.temp_dir, 'config1.yaml')
        yaml2 = os.path.join(self.temp_dir, 'config2.yaml')
        
        data1 = {'app_name': 'TestApp', 'version': '1.0.0'}
        data2 = {'debug': True, 'port': 8080}
        
        with open(yaml1, 'w') as f:
            yaml.dump(data1, f)
        with open(yaml2, 'w') as f:
            yaml.dump(data2, f)
        
        result = yamlfiles2dict(yaml1, yaml2)
        expected = {**data1, **data2}
        self.assertEqual(result, expected)
        
    def test_merge_dict(self):
        """Test dictionary merging"""
        dict1 = {
            'a': 1,
            'b': {'x': 10, 'y': 20}
        }
        dict2 = {
            'a': 2,
            'b': {'y': 30, 'z': 40},
            'c': 3
        }
        
        result = merge_dict(dict1, dict2)
        expected = {
            'a': 2,
            'b': {'x': 10, 'y': 30, 'z': 40},
            'c': 3
        }
        self.assertEqual(result, expected)
        
    def test_tcl_interpreter_basic(self):
        """Test basic Tcl interpreter operations"""
        interp = create_tcl_interp()
        
        # Test setting and getting variables
        test_dict = {'test_var': 'test_value', 'number': 42}
        dict2tclinterp(test_dict, interp)
        
        result = tclinterp2dict(interp)
        self.assertEqual(result['test_var'], 'test_value')
        self.assertEqual(result['number'], 42)
        
    def test_files2dict_mixed(self):
        """Test loading mixed YAML and Tcl files"""
        tcl_file = os.path.join(self.temp_dir, 'config.tcl')
        yaml_file = os.path.join(self.temp_dir, 'config.yaml')
        
        # Create Tcl file
        with open(tcl_file, 'w') as f:
            f.write("""
set environment "test"
set debug_mode 1
""")
        
        # Create YAML file
        yaml_data = {
            'app_name': 'TestApp',
            'features': ['feature1', 'feature2']
        }
        with open(yaml_file, 'w') as f:
            yaml.dump(yaml_data, f)
        
        result = files2dict(tcl_file, yaml_file)
        
        # Check that both Tcl and YAML data are present
        self.assertEqual(result['environment'], 'test')
        self.assertEqual(result['debug_mode'], 1)
        self.assertEqual(result['app_name'], 'TestApp')
        self.assertEqual(result['features'], ['feature1', 'feature2'])
        
    def test_yaml_to_tcl_conversion(self):
        """Test YAML to Tcl file conversion"""
        yaml_file = os.path.join(self.temp_dir, 'input.yaml')
        tcl_file = os.path.join(self.temp_dir, 'output.tcl')
        
        test_data = {
            'app_name': 'TestApp',
            'port': 8080,
            'config': {
                'debug': True,
                'timeout': 30
            }
        }
        
        with open(yaml_file, 'w') as f:
            yaml.dump(test_data, f)
        
        # Convert YAML to Tcl
        yamlfiles2tclfile(yaml_file, output_file=tcl_file)
        
        # Verify the Tcl file was created
        self.assertTrue(os.path.exists(tcl_file))
        
        # Verify the content by loading it back
        from configkit.core.tcl_interpreter import tclfiles2tclinterp
        interp = tclfiles2tclinterp(tcl_file)
        result = tclinterp2dict(interp)
        
        self.assertEqual(result['app_name'], 'TestApp')
        self.assertEqual(result['port'], 8080)
        self.assertEqual(result['config']['debug'], True)
        self.assertEqual(result['config']['timeout'], 30)
        
    def test_tcl_to_yaml_conversion(self):
        """Test Tcl to YAML file conversion"""
        tcl_file = os.path.join(self.temp_dir, 'input.tcl')
        yaml_file = os.path.join(self.temp_dir, 'output.yaml')
        
        with open(tcl_file, 'w') as f:
            f.write("""
set app_name "TestApp"
set port 8080
set config(debug) 1
set config(timeout) 30
""")
        
        # Convert Tcl to YAML
        tclfiles2yamlfile(tcl_file, output_file=yaml_file)
        
        # Verify the YAML file was created
        self.assertTrue(os.path.exists(yaml_file))
        
        # Verify the content by loading it back
        with open(yaml_file, 'r') as f:
            result = yaml.safe_load(f)
        
        self.assertEqual(result['app_name'], 'TestApp')
        self.assertEqual(result['port'], 8080)
        self.assertEqual(result['config']['debug'], 1)
        self.assertEqual(result['config']['timeout'], 30)

class TestErrorHandling(unittest.TestCase):
    
    def test_missing_file(self):
        """Test handling of missing files"""
        with self.assertRaises(FileNotFoundError):
            yamlfiles2dict('non_existent_file.yaml')
            
    def test_invalid_yaml(self):
        """Test handling of invalid YAML"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write('invalid: yaml: content: [')
            invalid_yaml = f.name
        
        try:
            with self.assertRaises(yaml.YAMLError):
                yamlfiles2dict(invalid_yaml)
        finally:
            os.unlink(invalid_yaml)
            
    def test_empty_file_list(self):
        """Test handling of empty file list"""
        with self.assertRaises(ValueError):
            files2dict()

if __name__ == '__main__':
    unittest.main() 
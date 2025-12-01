#!/usr/bin/env python3
"""
Use sensAI concepts to identify and categorize features in the kawaiigpt repository.
Then write the findings to Serena's memory system.
"""

import ast
import json
import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set

class FeatureCategorizer:
    """
    Categorize code features using sensAI-inspired feature engineering concepts.
    """
    
    def __init__(self):
        self.features = defaultdict(list)
        self.categories = {
            'installation': [],
            'configuration': [],
            'user_interface': [],
            'api_integration': [],
            'data_processing': [],
            'authentication': [],
            'utilities': [],
            'error_handling': [],
            'platform_detection': [],
            'dependency_management': [],
            'voice_processing': [],
            'translation': [],
            'cryptography': [],
        }
        
    def categorize_feature(self, feature_name: str, feature_type: str, context: Dict) -> str:
        """Categorize a feature based on its name, type, and context"""
        name_lower = feature_name.lower()
        
        # Installation features
        if any(keyword in name_lower for keyword in ['install', 'setup', 'package', 'dependencies']):
            return 'installation'
        
        # Platform detection
        if any(keyword in name_lower for keyword in ['detect', 'os', 'platform', 'termux', 'linux', 'android']):
            return 'platform_detection'
        
        # Configuration
        if any(keyword in name_lower for keyword in ['config', 'setting', 'mode', 'option']):
            return 'configuration'
        
        # UI features
        if any(keyword in name_lower for keyword in ['ui', 'interface', 'display', 'show', 'print', 'prompt']):
            return 'user_interface'
        
        # API integration
        if any(keyword in name_lower for keyword in ['api', 'request', 'http', 'client', 'fetch']):
            return 'api_integration'
        
        # Voice processing
        if any(keyword in name_lower for keyword in ['voice', 'tts', 'audio', 'sound', 'alsa', 'speak']):
            return 'voice_processing'
        
        # Translation
        if any(keyword in name_lower for keyword in ['translate', 'translation', 'language']):
            return 'translation'
        
        # Cryptography
        if any(keyword in name_lower for keyword in ['crypto', 'encrypt', 'decrypt', 'hash', 'secure']):
            return 'cryptography'
        
        # Data processing
        if any(keyword in name_lower for keyword in ['process', 'parse', 'transform', 'convert', 'generate']):
            return 'data_processing'
        
        # Error handling
        if any(keyword in name_lower for keyword in ['error', 'exception', 'try', 'catch', 'handle']):
            return 'error_handling'
        
        # Utilities
        if any(keyword in name_lower for keyword in ['util', 'helper', 'common', 'shared', 'base']):
            return 'utilities'
        
        return 'utilities'  # default
    
    def analyze_python_file(self, file_path: Path) -> Dict:
        """Analyze a Python file and extract features"""
        features = {
            'file': str(file_path),
            'functions': [],
            'classes': [],
            'imports': [],
            'variables': [],
            'features_by_category': defaultdict(list)
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Parse AST
            try:
                tree = ast.parse(content)
            except SyntaxError:
                # File might be obfuscated, use regex fallback
                return self._analyze_with_regex(file_path, content)
            
            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        features['imports'].append({
                            'module': alias.name,
                            'alias': alias.asname,
                            'type': 'import'
                        })
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        features['imports'].append({
                            'module': f"{module}.{alias.name}" if module else alias.name,
                            'alias': alias.asname,
                            'type': 'import_from'
                        })
            
            # Extract functions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = {
                        'name': node.name,
                        'line': node.lineno,
                        'args': [arg.arg for arg in node.args.args],
                        'decorators': [ast.unparse(d) if hasattr(ast, 'unparse') else str(d) for d in node.decorator_list],
                        'type': 'function'
                    }
                    features['functions'].append(func_info)
                    
                    # Categorize
                    category = self.categorize_feature(node.name, 'function', {'file': file_path.name})
                    features['features_by_category'][category].append({
                        'name': node.name,
                        'type': 'function',
                        'line': node.lineno
                    })
                    self.categories[category].append(func_info)
                
                elif isinstance(node, ast.ClassDef):
                    class_info = {
                        'name': node.name,
                        'line': node.lineno,
                        'bases': [ast.unparse(b) if hasattr(ast, 'unparse') else str(b) for b in node.bases],
                        'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                        'type': 'class'
                    }
                    features['classes'].append(class_info)
                    
                    # Categorize
                    category = self.categorize_feature(node.name, 'class', {'file': file_path.name})
                    features['features_by_category'][category].append({
                        'name': node.name,
                        'type': 'class',
                        'line': node.lineno
                    })
                    self.categories[category].append(class_info)
                
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            var_info = {
                                'name': target.id,
                                'line': node.lineno,
                                'type': 'variable'
                            }
                            features['variables'].append(var_info)
                            
                            # Categorize important variables
                            if len(target.id) > 3:  # Skip very short variable names
                                category = self.categorize_feature(target.id, 'variable', {'file': file_path.name})
                                if category != 'utilities':  # Only categorize non-utility variables
                                    features['features_by_category'][category].append(var_info)
        
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return self._analyze_with_regex(file_path, content if 'content' in locals() else '')
        
        return features
    
    def _analyze_with_regex(self, file_path: Path, content: str) -> Dict:
        """Fallback regex-based analysis for obfuscated files"""
        features = {
            'file': str(file_path),
            'functions': [],
            'classes': [],
            'imports': [],
            'variables': [],
            'features_by_category': defaultdict(list),
            'note': 'Regex-based analysis (file may be obfuscated)'
        }
        
        # Extract imports
        import_pattern = r'^(?:from\s+(\S+)\s+)?import\s+(\S+)'
        for match in re.finditer(import_pattern, content, re.MULTILINE):
            module = match.group(1) or match.group(2)
            features['imports'].append({
                'module': module,
                'type': 'import'
            })
        
        # Extract function definitions
        func_pattern = r'def\s+(\w+)\s*\('
        for match in re.finditer(func_pattern, content):
            func_name = match.group(1)
            features['functions'].append({
                'name': func_name,
                'type': 'function'
            })
            category = self.categorize_feature(func_name, 'function', {'file': file_path.name})
            features['features_by_category'][category].append({
                'name': func_name,
                'type': 'function'
            })
        
        # Extract class definitions
        class_pattern = r'class\s+(\w+)'
        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)
            features['classes'].append({
                'name': class_name,
                'type': 'class'
            })
            category = self.categorize_feature(class_name, 'class', {'file': file_path.name})
            features['features_by_category'][category].append({
                'name': class_name,
                'type': 'class'
            })
        
        return features
    
    def analyze_repository(self, repo_path: Path) -> Dict:
        """Analyze entire repository"""
        results = {
            'repository': str(repo_path),
            'files': [],
            'summary': {
                'total_functions': 0,
                'total_classes': 0,
                'total_imports': 0,
                'features_by_category': {}
            },
            'categories': {}
        }
        
        # Analyze Python files
        python_files = [
            repo_path / "install.py",
            repo_path / "kawai.py",
        ]
        
        all_features = []
        for py_file in python_files:
            if py_file.exists():
                file_features = self.analyze_python_file(py_file)
                results['files'].append(file_features)
                all_features.append(file_features)
                
                results['summary']['total_functions'] += len(file_features['functions'])
                results['summary']['total_classes'] += len(file_features['classes'])
                results['summary']['total_imports'] += len(file_features['imports'])
        
        # Aggregate by category
        for category, items in self.categories.items():
            if items:
                results['summary']['features_by_category'][category] = len(items)
                results['categories'][category] = items
        
        # Analyze dependencies from requirements.txt
        req_file = repo_path / "requirements.txt"
        if req_file.exists():
            with open(req_file, 'r') as f:
                requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            results['dependencies'] = requirements
            
            # Categorize dependencies
            dep_categories = defaultdict(list)
            for req in requirements:
                req_lower = req.lower().split('==')[0].split('>=')[0].split('<=')[0]
                if 'tts' in req_lower or 'audio' in req_lower or 'sound' in req_lower:
                    dep_categories['voice_processing'].append(req)
                elif 'translate' in req_lower:
                    dep_categories['translation'].append(req)
                elif 'crypto' in req_lower or 'crypt' in req_lower:
                    dep_categories['cryptography'].append(req)
                elif 'request' in req_lower or 'http' in req_lower:
                    dep_categories['api_integration'].append(req)
                elif 'toolkit' in req_lower or 'ui' in req_lower:
                    dep_categories['user_interface'].append(req)
                else:
                    dep_categories['utilities'].append(req)
            
            results['dependencies_by_category'] = dict(dep_categories)
        
        return results

def write_to_serena(results: Dict, repo_path: Path):
    """Write feature analysis results to Serena's memory system"""
    memories_dir = repo_path / ".serena" / "memories"
    memories_dir.mkdir(parents=True, exist_ok=True)
    
    # Create comprehensive feature analysis memory
    memory_content = f"""# KawaiiGPT Feature Analysis (sensAI-based)

## Executive Summary
This document provides a comprehensive feature categorization and identification analysis of the KawaiiGPT repository using sensAI-inspired feature engineering concepts.

### Repository Statistics
- Total Functions Identified: {results['summary']['total_functions']}
- Total Classes Identified: {results['summary']['total_classes']}
- Total Imports: {results['summary']['total_imports']}
- Files Analyzed: {len(results['files'])}

## Feature Categories

"""
    
    # Add category details
    for category, count in sorted(results['summary']['features_by_category'].items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            memory_content += f"### {category.replace('_', ' ').title()} ({count} features)\n\n"
            
            # List features in this category
            if category in results['categories']:
                features = results['categories'][category]
                for feature in features[:10]:  # Limit to first 10
                    memory_content += f"- **{feature.get('name', 'unknown')}** ({feature.get('type', 'unknown')})"
                    if 'line' in feature:
                        memory_content += f" - Line {feature['line']}"
                    memory_content += "\n"
                
                if len(features) > 10:
                    memory_content += f"- ... and {len(features) - 10} more\n"
            
            memory_content += "\n"
    
    # Add dependency analysis
    if 'dependencies_by_category' in results:
        memory_content += "\n## Dependencies by Category\n\n"
        for category, deps in results['dependencies_by_category'].items():
            memory_content += f"### {category.replace('_', ' ').title()}\n"
            for dep in deps:
                memory_content += f"- {dep}\n"
            memory_content += "\n"
    
    # Add file-level analysis
    memory_content += "\n## File-Level Feature Analysis\n\n"
    for file_info in results['files']:
        memory_content += f"### {Path(file_info['file']).name}\n\n"
        memory_content += f"- Functions: {len(file_info['functions'])}\n"
        memory_content += f"- Classes: {len(file_info['classes'])}\n"
        memory_content += f"- Imports: {len(file_info['imports'])}\n\n"
        
        # Show top categories for this file
        if file_info['features_by_category']:
            memory_content += "**Feature Categories:**\n"
            for cat, items in sorted(file_info['features_by_category'].items(), key=lambda x: len(x[1]), reverse=True)[:5]:
                memory_content += f"- {cat.replace('_', ' ').title()}: {len(items)} features\n"
        memory_content += "\n"
    
    # Write memory file
    memory_file = memories_dir / "sensai_feature_analysis.md"
    with open(memory_file, 'w') as f:
        f.write(memory_content)
    
    print(f"Feature analysis written to: {memory_file}")
    
    # Also create a JSON summary for programmatic access
    json_file = repo_path / "sensai_feature_analysis.json"
    with open(json_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Feature analysis JSON saved to: {json_file}")
    
    return memory_file, json_file

def main():
    repo_path = Path("/workspace/kawaiigpt")
    
    print("=== Running sensAI Feature Analysis ===")
    
    categorizer = FeatureCategorizer()
    results = categorizer.analyze_repository(repo_path)
    
    print(f"\n=== Analysis Complete ===")
    print(f"Functions found: {results['summary']['total_functions']}")
    print(f"Classes found: {results['summary']['total_classes']}")
    print(f"\nFeatures by category:")
    for category, count in sorted(results['summary']['features_by_category'].items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f"  {category}: {count}")
    
    print("\n=== Writing to Serena ===")
    memory_file, json_file = write_to_serena(results, repo_path)
    
    print(f"\n=== sensAI Feature Analysis Complete ===")
    print(f"Results written to Serena memory: {memory_file}")
    print(f"JSON summary: {json_file}")

if __name__ == "__main__":
    main()

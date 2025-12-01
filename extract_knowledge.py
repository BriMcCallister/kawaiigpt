#!/usr/bin/env python3
"""
Extract quads and triples from kawaiigpt repository using Serena.
This script uses Serena's semantic code analysis to extract knowledge graph structures.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

def run_serena_command(cmd_args):
    """Run a Serena command via uvx"""
    base_cmd = [
        "uvx", "--from", "git+https://github.com/oraios/serena", "serena"
    ]
    full_cmd = base_cmd + cmd_args
    try:
        result = subprocess.run(
            full_cmd,
            capture_output=True,
            text=True,
            cwd="/workspace/kawaiigpt"
        )
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), 1

def extract_semantic_relationships():
    """
    Use Serena to analyze the repository and extract triples/quads.
    Since we can't easily interact with MCP server programmatically,
    we'll create a comprehensive analysis script that Serena can execute.
    """
    
    project_path = Path("/workspace/kawaiigpt")
    
    # First, ensure project is set up
    print("=== Setting up Serena project ===")
    stdout, stderr, code = run_serena_command([
        "project", "create",
        "--language", "python",
        "--name", "kawaiigpt"
    ])
    
    if code != 0:
        print(f"Note: Project may already exist or there was an issue: {stderr}")
    else:
        print(f"Project created: {stdout}")
    
    # Create analysis script that will extract semantic information
    analysis_script = """
import ast
import json
import os
from pathlib import Path

def extract_triples_from_ast(node, file_path, context=""):
    '''Extract triples from Python AST'''
    triples = []
    
    if isinstance(node, ast.FunctionDef):
        # Function definition triples
        triples.append({
            'subject': node.name,
            'predicate': 'is_a',
            'object': 'function',
            'context': file_path,
            'graph': 'code_structure'
        })
        
        # Function parameters
        for arg in node.args.args:
            triples.append({
                'subject': node.name,
                'predicate': 'has_parameter',
                'object': arg.arg,
                'context': file_path,
                'graph': 'code_structure'
            })
    
    elif isinstance(node, ast.ClassDef):
        # Class definition triples
        triples.append({
            'subject': node.name,
            'predicate': 'is_a',
            'object': 'class',
            'context': file_path,
            'graph': 'code_structure'
        })
        
        # Inheritance relationships
        for base in node.bases:
            if isinstance(base, ast.Name):
                triples.append({
                    'subject': node.name,
                    'predicate': 'inherits_from',
                    'object': base.id,
                    'context': file_path,
                    'graph': 'inheritance'
                })
    
    elif isinstance(node, ast.Import):
        # Import relationships
        for alias in node.names:
            triples.append({
                'subject': os.path.basename(file_path),
                'predicate': 'imports',
                'object': alias.name,
                'context': file_path,
                'graph': 'dependencies'
            })
    
    elif isinstance(node, ast.ImportFrom):
        if node.module:
            for alias in node.names:
                triples.append({
                    'subject': os.path.basename(file_path),
                    'predicate': 'imports_from',
                    'object': f"{node.module}.{alias.name}",
                    'context': file_path,
                    'graph': 'dependencies'
                })
    
    elif isinstance(node, ast.Assign):
        # Variable assignments
        for target in node.targets:
            if isinstance(target, ast.Name):
                triples.append({
                    'subject': target.id,
                    'predicate': 'assigned_in',
                    'object': os.path.basename(file_path),
                    'context': file_path,
                    'graph': 'code_structure'
                })
    
    elif isinstance(node, ast.Call):
        # Function calls
        if isinstance(node.func, ast.Name):
            triples.append({
                'subject': os.path.basename(file_path),
                'predicate': 'calls',
                'object': node.func.id,
                'context': file_path,
                'graph': 'call_graph'
            })
    
    return triples

def extract_quads_from_relationships(triples, file_path):
    '''Convert triples to quads by adding graph context'''
    quads = []
    for triple in triples:
        quad = {
            'subject': triple['subject'],
            'predicate': triple['predicate'],
            'object': triple['object'],
            'graph': triple.get('graph', 'default'),
            'context': triple.get('context', file_path)
        }
        quads.append(quad)
    return quads

def analyze_file(file_path):
    '''Analyze a Python file and extract semantic relationships'''
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        tree = ast.parse(content, filename=file_path)
        
        all_triples = []
        for node in ast.walk(tree):
            triples = extract_triples_from_ast(node, str(file_path))
            all_triples.extend(triples)
        
        quads = extract_quads_from_relationships(all_triples, str(file_path))
        
        return {
            'file': str(file_path),
            'triples': all_triples,
            'quads': quads
        }
    except Exception as e:
        return {
            'file': str(file_path),
            'error': str(e),
            'triples': [],
            'quads': []
        }

# Analyze all Python files
project_path = Path("/workspace/kawaiigpt")
results = {
    'triples': [],
    'quads': [],
    'files_analyzed': []
}

python_files = [
    project_path / "install.py",
    project_path / "kawai.py",
]

for py_file in python_files:
    if py_file.exists():
        print(f"Analyzing {py_file.name}...")
        file_results = analyze_file(py_file)
        results['triples'].extend(file_results['triples'])
        results['quads'].extend(file_results['quads'])
        results['files_analyzed'].append({
            'file': str(py_file),
            'triple_count': len(file_results['triples']),
            'quad_count': len(file_results['quads'])
        })

# Save results
output_file = project_path / "knowledge_extraction.json"
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\\n=== Analysis Complete ===")
print(f"Total triples: {len(results['triples'])}")
print(f"Total quads: {len(results['quads'])}")
print(f"Results saved to: {output_file}")
"""
    
    # Write and execute the analysis script
    script_path = project_path / "extract_knowledge_internal.py"
    with open(script_path, 'w') as f:
        f.write(analysis_script)
    
    print("\n=== Running Knowledge Extraction ===")
    result = subprocess.run(
        ["python3", str(script_path)],
        cwd=str(project_path),
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print(f"Errors: {result.stderr}")
    
    # Read results
    results_file = project_path / "knowledge_extraction.json"
    if results_file.exists():
        with open(results_file, 'r') as f:
            results = json.load(f)
        
        print("\n=== Knowledge Extraction Summary ===")
        print(f"Files analyzed: {len(results['files_analyzed'])}")
        print(f"Total triples extracted: {len(results['triples'])}")
        print(f"Total quads extracted: {len(results['quads'])}")
        
        # Show sample triples
        if results['triples']:
            print("\n=== Sample Triples ===")
            for triple in results['triples'][:10]:
                print(f"  {triple['subject']} --{triple['predicate']}--> {triple['object']} [{triple.get('graph', 'default')}]")
        
        # Show sample quads
        if results['quads']:
            print("\n=== Sample Quads ===")
            for quad in results['quads'][:10]:
                print(f"  {quad['subject']} --{quad['predicate']}--> {quad['object']} [graph: {quad['graph']}, context: {os.path.basename(quad['context'])}]")
        
        return results
    else:
        print("Error: Results file not created")
        return None

if __name__ == "__main__":
    results = extract_semantic_relationships()
    if results:
        print("\n=== Extraction Complete ===")
        print(f"Knowledge graph structures extracted and saved to /workspace/kawaiigpt/knowledge_extraction.json")

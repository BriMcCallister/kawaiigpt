#!/usr/bin/env python3
"""
Script to use Serena to analyze the kawaiigpt repository and extract quads and triples.
This script uses Serena's tools programmatically to understand the codebase structure
and extract semantic relationships (triples: subject-predicate-object, quads: with context).
"""

import os
import sys
import json
from pathlib import Path

# Add serena to path
serena_path = Path("/workspace/serena/src")
sys.path.insert(0, str(serena_path))

try:
    from serena.agent import SerenaAgent
    from serena.config.context_mode import SerenaAgentContext, SerenaAgentMode
    from serena.config.serena_config import SerenaConfig
    from serena.tools import (
        OnboardingTool,
        FindSymbolTool,
        GetSymbolsOverviewTool,
        FindReferencingSymbolsTool,
        ReadFileTool,
        ListDirTool,
        SearchForPatternTool,
    )
except ImportError as e:
    print(f"Error importing Serena: {e}")
    print("Trying to use Serena via MCP server instead...")
    sys.exit(1)


def extract_triples_from_symbol(symbol_info, file_path, context=""):
    """
    Extract triples (subject-predicate-object) from symbol information.
    """
    triples = []
    
    symbol_name = symbol_info.get('name', '')
    symbol_kind = symbol_info.get('kind', '')
    symbol_location = symbol_info.get('location', {})
    
    # Triple: symbol - is_a - kind
    if symbol_name and symbol_kind:
        triples.append({
            'subject': symbol_name,
            'predicate': 'is_a',
            'object': symbol_kind,
            'context': file_path,
            'graph': context
        })
    
    # Triple: symbol - defined_in - file
    if symbol_name and file_path:
        triples.append({
            'subject': symbol_name,
            'predicate': 'defined_in',
            'object': file_path,
            'context': context,
            'graph': 'code_structure'
        })
    
    # Triple: symbol - located_at - location
    if symbol_name and symbol_location:
        line = symbol_location.get('line', 0)
        if line:
            triples.append({
                'subject': symbol_name,
                'predicate': 'located_at',
                'object': f"{file_path}:{line}",
                'context': context,
                'graph': 'code_structure'
            })
    
    return triples


def extract_quads_from_references(references, source_symbol, file_path, context=""):
    """
    Extract quads (subject-predicate-object-graph) from reference relationships.
    """
    quads = []
    
    for ref in references:
        ref_symbol = ref.get('name', '')
        ref_file = ref.get('location', {}).get('file', '')
        ref_kind = ref.get('kind', '')
        
        if ref_symbol and source_symbol:
            # Quad: source_symbol - references - ref_symbol - in_context
            quads.append({
                'subject': source_symbol,
                'predicate': 'references',
                'object': ref_symbol,
                'graph': f"{file_path}->{ref_file}",
                'context': context
            })
            
            # Quad: ref_symbol - referenced_by - source_symbol - in_context
            quads.append({
                'subject': ref_symbol,
                'predicate': 'referenced_by',
                'object': source_symbol,
                'graph': f"{ref_file}->{file_path}",
                'context': context
            })
    
    return quads


def analyze_repository_with_serena(project_path):
    """
    Use Serena to analyze the repository and extract semantic relationships.
    """
    print(f"Initializing Serena agent for project: {project_path}")
    
    # Initialize Serena agent
    config = SerenaConfig(web_dashboard=False, log_level="INFO")
    context = SerenaAgentContext.load("ide-assistant")
    mode = SerenaAgentMode.load("onboarding")
    
    agent = SerenaAgent(
        project=str(project_path),
        serena_config=config,
        context=context,
        modes=[mode],
    )
    
    print("Serena agent initialized successfully")
    
    # Perform onboarding
    print("\n=== Performing Onboarding ===")
    onboarding_tool = agent.get_tool(OnboardingTool)
    onboarding_result = onboarding_tool.apply()
    print(f"Onboarding instructions: {onboarding_result[:500]}...")
    
    # Get all Python files
    print("\n=== Discovering Python Files ===")
    list_dir_tool = agent.get_tool(ListDirTool)
    files_result = list_dir_tool.apply(project_path, recursive=True)
    print(f"Found files: {files_result[:200]}...")
    
    # Extract triples and quads
    all_triples = []
    all_quads = []
    
    # Analyze main files
    python_files = [
        "kawai.py",
        "install.py",
    ]
    
    for filename in python_files:
        file_path = os.path.join(project_path, filename)
        if not os.path.exists(file_path):
            continue
            
        print(f"\n=== Analyzing {filename} ===")
        
        # Get symbols overview
        try:
            symbols_tool = agent.get_tool(GetSymbolsOverviewTool)
            symbols_result = symbols_tool.apply(file_path)
            print(f"Symbols in {filename}: {symbols_result[:300]}...")
            
            # Parse symbols (this is a simplified version - actual parsing would be more complex)
            # For now, we'll extract what we can from the text output
            
        except Exception as e:
            print(f"Error analyzing {filename}: {e}")
        
        # Find symbols
        try:
            find_symbol_tool = agent.get_tool(FindSymbolTool)
            # Search for common patterns
            for pattern in ["def ", "class ", "import "]:
                try:
                    symbols = find_symbol_tool.apply(pattern, file_path=file_path)
                    print(f"Found symbols matching '{pattern}': {symbols[:200]}...")
                except Exception as e:
                    print(f"Error searching for '{pattern}': {e}")
        except Exception as e:
            print(f"Error in symbol search: {e}")
    
    # Save results
    results = {
        'triples': all_triples,
        'quads': all_quads,
        'onboarding': onboarding_result,
    }
    
    output_file = os.path.join(project_path, "serena_analysis.json")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n=== Analysis Complete ===")
    print(f"Results saved to: {output_file}")
    print(f"Total triples extracted: {len(all_triples)}")
    print(f"Total quads extracted: {len(all_quads)}")
    
    return results


if __name__ == "__main__":
    project_path = Path("/workspace/kawaiigpt")
    if not project_path.exists():
        print(f"Error: Project path does not exist: {project_path}")
        sys.exit(1)
    
    try:
        results = analyze_repository_with_serena(project_path)
        print("\n=== Summary ===")
        print(json.dumps(results, indent=2)[:1000])
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

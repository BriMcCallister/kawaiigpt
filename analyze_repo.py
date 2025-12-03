#!/usr/bin/env python3
"""
Analyze the kawaiigpt repository using Serena's tools.
Extract knowledge in the form of triples and quads.
"""
import json
import sys
import os

# Add serena to path
sys.path.insert(0, '/workspace/serena/src')

from serena.agent import SerenaAgent
from serena.tools.file_tools import ListDirTool, ReadFileTool, SearchForPatternTool
from serena.tools.symbol_tools import GetSymbolsOverviewTool, FindSymbolTool
from serena.tools.memory_tools import WriteMemoryTool, ListMemoriesTool


def extract_triples_from_code(agent, filepath: str) -> list[dict]:
    """Extract semantic triples from code analysis."""
    triples = []
    
    # Get symbols overview
    overview_tool = agent.get_tool(GetSymbolsOverviewTool)
    try:
        result = overview_tool.apply(filepath)
        if result and "error" not in result.lower():
            # Parse symbols and create triples
            triples.append({
                "subject": filepath,
                "predicate": "hasSymbolsOverview",
                "object": result[:500]  # Truncate for readability
            })
    except Exception as e:
        triples.append({
            "subject": filepath,
            "predicate": "analysisError",
            "object": str(e)
        })
    
    return triples


def analyze_project_structure(agent, project_path: str) -> dict:
    """Analyze the project structure and extract metadata."""
    analysis = {
        "project_path": project_path,
        "files": [],
        "triples": [],
        "quads": []
    }
    
    # List directory contents
    list_dir_tool = agent.get_tool(ListDirTool)
    try:
        dir_content = list_dir_tool.apply(project_path, recursive=True)
        analysis["directory_structure"] = dir_content
        
        # Create triple for project structure
        analysis["triples"].append({
            "subject": project_path,
            "predicate": "hasDirectoryStructure",
            "object": dir_content[:1000]
        })
    except Exception as e:
        print(f"Error listing directory: {e}")
    
    return analysis


def read_and_analyze_files(agent, project_path: str, analysis: dict) -> dict:
    """Read and analyze key files."""
    read_file_tool = agent.get_tool(ReadFileTool)
    
    key_files = ["README.md", "install.py", "requirements.txt"]
    
    for filename in key_files:
        filepath = f"{filename}"
        try:
            content = read_file_tool.apply(filepath)
            if content and "not found" not in content.lower() and "error" not in content.lower():
                analysis["files"].append({
                    "path": filepath,
                    "content_preview": content[:500]
                })
                
                # Create triples
                analysis["triples"].append({
                    "subject": project_path,
                    "predicate": "containsFile",
                    "object": filepath
                })
                
                # Create quad (with context)
                analysis["quads"].append({
                    "subject": filepath,
                    "predicate": "hasContent",
                    "object": content[:200],
                    "context": "kawaiigpt_project_analysis"
                })
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
    
    return analysis


def search_for_patterns(agent, analysis: dict) -> dict:
    """Search for important patterns in the codebase."""
    search_tool = agent.get_tool(SearchForPatternTool)
    
    patterns = ["import", "def ", "class ", "API", "GPT", "openai"]
    
    for pattern in patterns:
        try:
            result = search_tool.apply(pattern)
            if result and "no matches" not in result.lower():
                analysis["triples"].append({
                    "subject": "kawaiigpt",
                    "predicate": f"containsPattern_{pattern.replace(' ', '_')}",
                    "object": result[:300]
                })
        except Exception as e:
            print(f"Error searching for pattern '{pattern}': {e}")
    
    return analysis


def save_memories(agent, analysis: dict):
    """Save analysis results to Serena memories."""
    write_memory_tool = agent.get_tool(WriteMemoryTool)
    
    # Save project overview
    overview_content = f"""# kawaiigpt Project Overview

## Project Analysis Date
{os.popen('date').read().strip()}

## Directory Structure
{analysis.get('directory_structure', 'Not available')[:2000]}

## Key Files Analyzed
{json.dumps([f['path'] for f in analysis.get('files', [])], indent=2)}

## Knowledge Triples Extracted
{json.dumps(analysis.get('triples', [])[:20], indent=2)}

## Knowledge Quads Extracted (with context)
{json.dumps(analysis.get('quads', [])[:10], indent=2)}
"""
    
    try:
        write_memory_tool.apply("project_overview.md", overview_content)
        print("Saved project_overview.md memory")
    except Exception as e:
        print(f"Error saving project overview: {e}")
    
    # Save triples/quads as structured data
    kg_content = f"""# Knowledge Graph Data

## Triples (Subject-Predicate-Object)
```json
{json.dumps(analysis.get('triples', []), indent=2)}
```

## Quads (Subject-Predicate-Object-Context)
```json
{json.dumps(analysis.get('quads', []), indent=2)}
```
"""
    
    try:
        write_memory_tool.apply("knowledge_graph.md", kg_content)
        print("Saved knowledge_graph.md memory")
    except Exception as e:
        print(f"Error saving knowledge graph: {e}")


def main():
    project_path = "/workspace/kawaiigpt"
    
    print("=" * 60)
    print("Serena Analysis of kawaiigpt Repository")
    print("=" * 60)
    
    # Initialize Serena agent
    print("\n1. Initializing Serena agent...")
    try:
        agent = SerenaAgent(project=project_path)
        print(f"   Agent initialized for project: {project_path}")
    except Exception as e:
        print(f"   Error initializing agent: {e}")
        return
    
    # Analyze project structure
    print("\n2. Analyzing project structure...")
    analysis = analyze_project_structure(agent, project_path)
    print(f"   Found directory structure")
    
    # Read and analyze files
    print("\n3. Reading and analyzing key files...")
    analysis = read_and_analyze_files(agent, project_path, analysis)
    print(f"   Analyzed {len(analysis['files'])} files")
    
    # Search for patterns
    print("\n4. Searching for patterns...")
    analysis = search_for_patterns(agent, analysis)
    print(f"   Extracted {len(analysis['triples'])} triples")
    print(f"   Extracted {len(analysis['quads'])} quads")
    
    # Save memories
    print("\n5. Saving memories...")
    save_memories(agent, analysis)
    
    # Print summary
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"\nTriples extracted: {len(analysis['triples'])}")
    print(f"Quads extracted: {len(analysis['quads'])}")
    print(f"\nSample triples:")
    for triple in analysis['triples'][:5]:
        print(f"  - {triple['subject']} --[{triple['predicate']}]--> {triple['object'][:50]}...")
    
    # Save full analysis to file
    output_file = "/workspace/kawaiigpt/.serena/analysis_output.json"
    with open(output_file, 'w') as f:
        json.dump(analysis, f, indent=2, default=str)
    print(f"\nFull analysis saved to: {output_file}")
    
    return analysis


if __name__ == "__main__":
    main()

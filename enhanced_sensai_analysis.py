#!/usr/bin/env python3
"""
Enhanced sensAI feature analysis that infers features from imports and dependencies
for obfuscated code, then writes comprehensive results to Serena.
"""

import json
from pathlib import Path
from collections import defaultdict

def infer_features_from_imports(imports: list) -> dict:
    """Infer feature categories from import statements"""
    inferred_features = defaultdict(list)
    
    for imp in imports:
        module = imp.get('module', '').lower()
        
        # Cryptography features
        if any(keyword in module for keyword in ['crypto', 'hashlib', 'base64', 'zlib']):
            inferred_features['cryptography'].append({
                'type': 'import',
                'module': imp['module'],
                'inference': 'Code obfuscation/encryption capabilities'
            })
        
        # System/OS features
        if any(keyword in module for keyword in ['os', 'sys', 'warnings']):
            inferred_features['system_integration'].append({
                'type': 'import',
                'module': imp['module'],
                'inference': 'System-level operations'
            })
        
        # Type system features
        if 'types' in module or 'builtins' in module:
            inferred_features['type_system'].append({
                'type': 'import',
                'module': imp['module'],
                'inference': 'Dynamic type manipulation (common in obfuscated code)'
            })
    
    return dict(inferred_features)

def create_comprehensive_feature_analysis():
    """Create comprehensive feature analysis combining AST analysis and inference"""
    
    repo_path = Path("/workspace/kawaiigpt")
    
    # Load existing analysis
    existing_file = repo_path / "sensai_feature_analysis.json"
    if existing_file.exists():
        with open(existing_file, 'r') as f:
            existing = json.load(f)
    else:
        existing = {'files': [], 'summary': {}, 'dependencies': []}
    
    # Enhanced analysis
    enhanced = {
        'repository': str(repo_path),
        'analysis_method': 'sensAI-inspired feature engineering',
        'files_analyzed': existing.get('files', []),
        'feature_categories': {},
        'inferred_features': {},
        'dependency_features': {},
        'comprehensive_categorization': {}
    }
    
    # Analyze imports from kawai.py (obfuscated file)
    kawai_file = next((f for f in existing['files'] if 'kawai.py' in f['file']), None)
    if kawai_file:
        imports = kawai_file.get('imports', [])
        enhanced['inferred_features'] = infer_features_from_imports(imports)
    
    # Categorize dependencies more comprehensively
    dep_features = defaultdict(list)
    for dep in existing.get('dependencies', []):
        dep_lower = dep.lower().split('==')[0]
        
        if 'tts' in dep_lower or 'audio' in dep_lower or 'sound' in dep_lower:
            dep_features['voice_processing'].append({
                'dependency': dep,
                'capability': 'Text-to-speech and audio playback'
            })
        elif 'translate' in dep_lower:
            dep_features['translation'].append({
                'dependency': dep,
                'capability': 'Multi-language translation'
            })
        elif 'crypto' in dep_lower:
            dep_features['cryptography'].append({
                'dependency': dep,
                'capability': 'Encryption and cryptographic operations'
            })
        elif 'request' in dep_lower:
            dep_features['api_integration'].append({
                'dependency': dep,
                'capability': 'HTTP requests and API communication'
            })
        elif 'toolkit' in dep_lower or 'prompt' in dep_lower:
            dep_features['user_interface'].append({
                'dependency': dep,
                'capability': 'Interactive command-line interface'
            })
        elif 'useragent' in dep_lower:
            dep_features['api_integration'].append({
                'dependency': dep,
                'capability': 'HTTP client spoofing/user agent rotation'
            })
        elif 'colorama' in dep_lower:
            dep_features['user_interface'].append({
                'dependency': dep,
                'capability': 'Colored terminal output'
            })
        elif 'regex' in dep_lower:
            dep_features['data_processing'].append({
                'dependency': dep,
                'capability': 'Pattern matching and text processing'
            })
        elif 'pexpect' in dep_lower:
            dep_features['system_integration'].append({
                'dependency': dep,
                'capability': 'Process automation and interaction'
            })
        elif 'pydub' in dep_lower:
            dep_features['data_processing'].append({
                'dependency': dep,
                'capability': 'Audio file manipulation'
            })
        else:
            dep_features['utilities'].append({
                'dependency': dep,
                'capability': 'General utility functionality'
            })
    
    enhanced['dependency_features'] = dict(dep_features)
    
    # Create comprehensive categorization
    comprehensive = {
        'core_features': {
            'installation_management': {
                'description': 'Automated dependency installation and environment setup',
                'components': ['install.py:up_package', 'install.py:pip_install', 'install.py:install_modules'],
                'category': 'installation'
            },
            'platform_detection': {
                'description': 'Cross-platform compatibility detection (Termux/Linux/Android)',
                'components': ['install.py:detect_os', 'install.py:check'],
                'category': 'platform_detection'
            },
            'code_obfuscation': {
                'description': 'Code protection and obfuscation (kawai.py is obfuscated)',
                'components': ['kawai.py:obfuscated_code', 'Crypto.Cipher.AES', 'base64', 'zlib', 'hashlib'],
                'category': 'cryptography',
                'note': 'Main application code is obfuscated for protection'
            }
        },
        'application_features': {
            'ai_chatbot': {
                'description': 'AI-powered conversational interface',
                'components': ['kawai.py (obfuscated)', 'prompt_toolkit'],
                'category': 'user_interface',
                'inferred': True
            },
            'voice_interaction': {
                'description': 'Text-to-speech and voice output capabilities',
                'components': ['edge_tts', 'simpleaudio', 'pydub'],
                'category': 'voice_processing',
                'note': 'ALSA library support mentioned in README'
            },
            'translation_service': {
                'description': 'Multi-language translation support',
                'components': ['deep_translator'],
                'category': 'translation'
            },
            'api_communication': {
                'description': 'HTTP API communication and request handling',
                'components': ['requests', 'fake_useragent'],
                'category': 'api_integration'
            },
            'interactive_ui': {
                'description': 'Rich command-line interface with tables and colors',
                'components': ['prompt_toolkit', 'liner-tables', 'colorama'],
                'category': 'user_interface'
            },
            'data_processing': {
                'description': 'Text processing and pattern matching',
                'components': ['regex'],
                'category': 'data_processing'
            },
            'system_automation': {
                'description': 'Process automation and system interaction',
                'components': ['pexpect'],
                'category': 'system_integration'
            }
        },
        'security_features': {
            'code_protection': {
                'description': 'Code obfuscation and encryption',
                'components': ['pycryptodome', 'AES encryption', 'base64 encoding'],
                'category': 'cryptography'
            },
            'request_spoofing': {
                'description': 'User agent rotation for API requests',
                'components': ['fake_useragent'],
                'category': 'api_integration'
            }
        },
        'platform_support': {
            'linux': {
                'description': 'Linux distribution support',
                'components': ['install.py:package_linux', 'apt-get commands'],
                'category': 'platform_detection'
            },
            'termux': {
                'description': 'Termux (Android) support',
                'components': ['install.py:package_termux', 'pkg commands'],
                'category': 'platform_detection'
            },
            'android': {
                'description': 'Android device detection and compatibility',
                'components': ['install.py:check (Android detection)', 'ALSA library considerations'],
                'category': 'platform_detection'
            }
        }
    }
    
    enhanced['comprehensive_categorization'] = comprehensive
    
    # Aggregate all features by category
    all_categories = defaultdict(list)
    
    # From existing analysis
    for category, items in existing.get('categories', {}).items():
        all_categories[category].extend(items)
    
    # From inferred features
    for category, items in enhanced['inferred_features'].items():
        all_categories[category].extend(items)
    
    # From dependencies
    for category, items in enhanced['dependency_features'].items():
        all_categories[category].extend([item['dependency'] for item in items])
    
    enhanced['feature_categories'] = {k: v for k, v in all_categories.items() if v}
    
    return enhanced

def write_enhanced_to_serena(enhanced_analysis: dict):
    """Write enhanced feature analysis to Serena memory"""
    
    repo_path = Path("/workspace/kawaiigpt")
    memories_dir = repo_path / ".serena" / "memories"
    memories_dir.mkdir(parents=True, exist_ok=True)
    
    memory_content = f"""# Enhanced sensAI Feature Categorization - KawaiiGPT

## Analysis Overview
This document provides a comprehensive feature identification and categorization analysis using sensAI-inspired feature engineering methodologies. The analysis combines AST parsing, import inference, and dependency analysis to create a complete feature taxonomy.

## Feature Categories Summary

"""
    
    # Add category summaries
    for category, items in sorted(enhanced_analysis['feature_categories'].items(), key=lambda x: len(x[1]), reverse=True):
        memory_content += f"### {category.replace('_', ' ').title()} ({len(items)} items)\n\n"
        for item in items[:5]:  # Show first 5
            if isinstance(item, dict):
                name = item.get('name', item.get('module', item.get('dependency', 'unknown')))
                memory_content += f"- {name}\n"
            else:
                memory_content += f"- {item}\n"
        if len(items) > 5:
            memory_content += f"- ... and {len(items) - 5} more\n"
        memory_content += "\n"
    
    # Add comprehensive categorization
    memory_content += "\n## Comprehensive Feature Categorization\n\n"
    
    for section, features in enhanced_analysis['comprehensive_categorization'].items():
        memory_content += f"### {section.replace('_', ' ').title()}\n\n"
        for feature_name, feature_info in features.items():
            memory_content += f"#### {feature_name.replace('_', ' ').title()}\n"
            memory_content += f"- **Description**: {feature_info['description']}\n"
            memory_content += f"- **Category**: {feature_info['category']}\n"
            if 'components' in feature_info:
                memory_content += f"- **Components**: {', '.join(feature_info['components'][:5])}\n"
            if 'note' in feature_info:
                memory_content += f"- **Note**: {feature_info['note']}\n"
            memory_content += "\n"
    
    # Add dependency features
    memory_content += "\n## Dependency-Based Feature Inference\n\n"
    for category, deps in enhanced_analysis['dependency_features'].items():
        memory_content += f"### {category.replace('_', ' ').title()}\n\n"
        for dep_info in deps:
            memory_content += f"- **{dep_info['dependency']}**: {dep_info['capability']}\n"
        memory_content += "\n"
    
    # Add inferred features from obfuscated code
    if enhanced_analysis['inferred_features']:
        memory_content += "\n## Inferred Features from Obfuscated Code\n\n"
        memory_content += "The main application file (kawai.py) is obfuscated. The following features were inferred from import statements:\n\n"
        for category, items in enhanced_analysis['inferred_features'].items():
            memory_content += f"### {category.replace('_', ' ').title()}\n\n"
            for item in items:
                memory_content += f"- **{item['module']}**: {item['inference']}\n"
            memory_content += "\n"
    
    # Write memory file
    memory_file = memories_dir / "enhanced_sensai_feature_analysis.md"
    with open(memory_file, 'w') as f:
        f.write(memory_content)
    
    print(f"Enhanced feature analysis written to: {memory_file}")
    
    # Save JSON
    json_file = repo_path / "enhanced_sensai_analysis.json"
    with open(json_file, 'w') as f:
        json.dump(enhanced_analysis, f, indent=2)
    
    print(f"Enhanced analysis JSON saved to: {json_file}")
    
    return memory_file, json_file

def main():
    print("=== Creating Enhanced sensAI Feature Analysis ===")
    
    enhanced = create_comprehensive_feature_analysis()
    
    print(f"\n=== Feature Categories Identified ===")
    for category, items in sorted(enhanced['feature_categories'].items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  {category}: {len(items)} items")
    
    print("\n=== Writing Enhanced Analysis to Serena ===")
    memory_file, json_file = write_enhanced_to_serena(enhanced)
    
    print(f"\n=== Enhanced sensAI Analysis Complete ===")
    print(f"Memory file: {memory_file}")
    print(f"JSON file: {json_file}")

if __name__ == "__main__":
    main()

import os
import csv
import time
import base64
from pathlib import Path
import pandas as pd
import requests
import tempfile
import subprocess
import shutil
from google import genai
from tqdm import tqdm
import re
import json
from collections import Counter
import networkx as nx
from datetime import datetime

# Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Set up API clients
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Configure Gemini
client = genai.Client(api_key=GEMINI_API_KEY)

# Technical sustainability patterns to look for (from SusAF)
SUSTAINABLE_PATTERNS = {
    'documentation': [
        r'"""[\s\S]*?"""',  # Python docstrings
        r'/\*\*[\s\S]*?\*/',  # JSDoc comments
        r'/// <summary>[\s\S]*?</summary>',  # C# XML comments
        r'#\s*@param',  # Parameter documentation
        r'#\s*@return',  # Return value documentation
    ],
    'testing': [
        r'import\s+[\'"]testing[\'"]',
        r'import\s+[\'"]pytest[\'"]',
        r'import\s+[\'"]unittest[\'"]',
        r'@Test',
        r'test\w*\([^)]*\)\s*{',
        r'assert\w*\(',  # Assertions in tests
        r'expect\(',  # Expectations in tests
        r'mock\w*\(',  # Mocking in tests
    ],
    'modularity': [
        r'import\s+',
        r'from\s+[\w.]+\s+import',
        r'require\([\'"]',
        r'export\s+',
        r'class\s+\w+',  # Class definitions
        r'interface\s+\w+',  # Interface definitions
        r'function\s+\w+',  # Function definitions
        r'def\s+\w+',  # Python function definitions
    ],
    'error_handling': [
        r'try\s*{',
        r'try:',
        r'catch\s*\(',
        r'except',
        r'finally',
        r'throw\s+new\s+\w+',
        r'raise\s+',
        r'error\w*\s*=',  # Error variable assignments
        r'log\w*\s*\(\s*[\'"]error',  # Error logging
        r'console\.error',  # Console error logging
    ],
    'config_management': [
        r'\.env',
        r'config\.',
        r'process\.env',
        r'os\.environ',
        r'settings\.',  # Settings modules
        r'constants\.',  # Constants
        r'getenv\(',  # Environment variable access
    ],
    'adaptability': [
        r'interface\s+\w+',  # Interfaces for adaptability
        r'abstract\s+class',  # Abstract classes
        r'extends\s+\w+',  # Inheritance
        r'implements\s+\w+',  # Interface implementation
        r'@Override',  # Method overriding
        r'super\(',  # Parent class method calls
        r'factory\.',  # Factory pattern usage
    ],
    'security': [
        r'sanitize',  # Input sanitization
        r'validate',  # Input validation
        r'escape',  # Output escaping
        r'authenticate',  # Authentication
        r'authorize',  # Authorization
        r'encrypt',  # Encryption
        r'decrypt',  # Decryption
        r'hash',  # Hashing
        r'token',  # Token usage
        r'permission',  # Permission checks
    ],
    'scalability': [
        r'cache',  # Caching
        r'pool',  # Connection pooling
        r'queue',  # Queue usage
        r'async',  # Asynchronous code
        r'await',  # Await keyword
        r'parallel',  # Parallel processing
        r'concurrent',  # Concurrent processing
        r'thread',  # Threading
        r'worker',  # Worker processes/threads
    ]
}

UNSUSTAINABLE_PATTERNS = {
    'code_smells': [
        r'TODO',
        r'FIXME',
        r'HACK',
        r'XXX',
        r'WTF',  # More code smells
        r'NOSONAR',  # SonarQube suppression
        r'CHECKSTYLE:OFF',  # Checkstyle suppression
    ],
    'hard_coding': [
        r'API_KEY\s*=\s*[\'"][^\'"]+[\'"]',
        r'password\s*=\s*[\'"][^\'"]+[\'"]',
        r'SECRET\s*=\s*[\'"][^\'"]+[\'"]',
        r'http[s]?://[^\s<>"\']+',  # Hardcoded URLs
        r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}',  # IP addresses
    ],
    'long_methods': [
        r'function\s+\w+\([^)]*\)\s*{[\s\S]{1000,}}',
        r'def\s+\w+\([^)]*\)[\s\S]{1000,}return',
        r'public\s+\w+\s+\w+\([^)]*\)\s*{[\s\S]{1000,}}',  # Java/C# methods
    ],
    'deep_nesting': [
        r'if\s*\([^)]+\)\s*{\s*if\s*\([^)]+\)\s*{\s*if',
        r'for\s*\([^)]+\)\s*{\s*for\s*\([^)]+\)\s*{\s*for',  # Nested loops
        r'while\s*\([^)]+\)\s*{\s*while\s*\([^)]+\)\s*{\s*while',  # Nested while loops
    ],
    'large_classes': [
        r'class\s+\w+[^{]*{[\s\S]{3000,}}',  # Large classes (>3000 chars)
    ],
    'naming_issues': [
        r'\b[a-z]{1,2}\b',  # Very short variable names
        r'\b[A-Z0-9_]+\b',  # CONSTANTS used as variables
    ],
    'commented_code': [
        r'//\s*[a-zA-Z0-9]+\s*\([^)]*\)',  # Commented out function calls
        r'//\s*if\s*\(',  # Commented out if statements
        r'//\s*for\s*\(',  # Commented out for loops
        r'#\s*[a-zA-Z0-9]+\s*\([^)]*\)',  # Python commented out function calls
    ]
}

# Environmental sustainability indicators
ENVIRONMENTAL_INDICATORS = {
    'high_computation': [
        r'train\(',  # ML model training
        r'fit\(',  # ML model fitting
        r'\.cuda',  # GPU usage
        r'gpu',  # GPU related code
        r'tensorflow',  # TensorFlow usage
        r'torch',  # PyTorch usage
        r'while\s*\(\s*true',  # Infinite loops
    ],
    'resource_efficient': [
        r'yield',  # Generators for memory efficiency
        r'streaming',  # Streaming APIs
        r'lazy',  # Lazy evaluation
        r'throttle',  # Rate limiting
        r'debounce',  # Debouncing
    ],
    'energy_awareness': [
        r'power',  # Power management
        r'battery',  # Battery optimization
        r'energy',  # Energy management
        r'sleep',  # Sleep modes
    ]
}

# Social sustainability indicators
SOCIAL_INDICATORS = {
    'inclusive_design': [
        r'a11y',  # Accessibility
        r'accessibility',  # Accessibility
        r'aria-',  # ARIA attributes
        r'alt=',  # Alt text for images
        r'i18n',  # Internationalization
        r'l10n',  # Localization
    ],
    'privacy_focused': [
        r'gdpr',  # GDPR compliance
        r'consent',  # User consent
        r'privacy',  # Privacy consideration
        r'anonymize',  # Data anonymization
        r'pseudonymize',  # Data pseudonymization
    ],
    'ethical_considerations': [
        r'ethic',  # Ethics
        r'bias',  # Bias consideration
        r'fairness',  # Fairness consideration
        r'diversity',  # Diversity consideration
        r'inclusion',  # Inclusion consideration
    ]
}

def clone_repo(repo_url, target_dir):
    """Clone a GitHub repository to a local directory"""
    try:
        subprocess.run(["git", "clone", repo_url, target_dir], 
                      check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository: {e}")
        return False

def get_code_files(repo_dir, exclude_dirs=None):
    """Get all relevant code files from the repository"""
    if exclude_dirs is None:
        exclude_dirs = ['node_modules', '.git', 'vendor', '__pycache__', 'build', 'dist', 'venv', 'env', '.venv']
    
    code_extensions = ['.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cs', '.go', '.rb', '.php', '.cpp', '.c', '.h', '.swift', '.kt', '.rs']
    files = []
    
    for root, dirs, filenames in os.walk(repo_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for filename in filenames:
            if any(filename.endswith(ext) for ext in code_extensions):
                files.append(os.path.join(root, filename))
    
    return files

def analyze_code_patterns(files):
    """Analyze code files for sustainable and unsustainable patterns"""
    results = {
        'sustainable': {k: 0 for k in SUSTAINABLE_PATTERNS},
        'unsustainable': {k: 0 for k in UNSUSTAINABLE_PATTERNS},
        'environmental': {k: 0 for k in ENVIRONMENTAL_INDICATORS},
        'social': {k: 0 for k in SOCIAL_INDICATORS},
        'total_lines': 0,
        'file_count': len(files),
        'file_types': Counter(),
        'avg_file_size': 0,
        'function_count': 0,
        'class_count': 0,
        'comment_ratio': 0
    }
    
    total_size = 0
    total_comment_lines = 0
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Count lines
            lines = content.split('\n')
            line_count = len(lines)
            results['total_lines'] += line_count
            
            # Calculate file size
            file_size = os.path.getsize(file_path)
            total_size += file_size
            
            # Count comment lines
            comment_patterns = [r'^\s*#', r'^\s*//', r'^\s*/\*', r'^\s*\*', r'^\s*\*/']
            comment_lines = sum(1 for line in lines if any(re.match(pattern, line) for pattern in comment_patterns))
            total_comment_lines += comment_lines
            
            # Count functions and classes
            function_matches = len(re.findall(r'(function\s+\w+|def\s+\w+)', content))
            class_matches = len(re.findall(r'(class\s+\w+)', content))
            results['function_count'] += function_matches
            results['class_count'] += class_matches
            
            # Count file types
            ext = os.path.splitext(file_path)[1]
            results['file_types'][ext] += 1
            
            # Check for sustainable patterns
            for category, patterns in SUSTAINABLE_PATTERNS.items():
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    results['sustainable'][category] += len(matches)
            
            # Check for unsustainable patterns
            for category, patterns in UNSUSTAINABLE_PATTERNS.items():
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    results['unsustainable'][category] += len(matches)
            
            # Check for environmental indicators
            for category, patterns in ENVIRONMENTAL_INDICATORS.items():
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    results['environmental'][category] += len(matches)
            
            # Check for social indicators
            for category, patterns in SOCIAL_INDICATORS.items():
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    results['social'][category] += len(matches)
                    
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
    
    # Calculate averages
    if len(files) > 0:
        results['avg_file_size'] = total_size / len(files)
        
    if results['total_lines'] > 0:
        results['comment_ratio'] = total_comment_lines / results['total_lines']
    
    return results

def calculate_cyclomatic_complexity(repo_dir):
    """Estimate cyclomatic complexity using radon for Python files"""
    complexity_data = {
        "average": 0, 
        "max": 0, 
        "complex_functions": 0,
        "maintainability_index": 0,
        "halstead_metrics": {
            "volume": 0,
            "difficulty": 0,
            "effort": 0
        }
    }
    
    try:
        # Check if radon is available
        result = subprocess.run(["pip", "show", "radon"], capture_output=True, text=True)
        if "not found" in result.stderr:
            subprocess.run(["pip", "install", "radon"], check=True)
        
        # Run radon on Python files for cyclomatic complexity
        result = subprocess.run(
            ["radon", "cc", repo_dir, "--average", "--total-average", "-s"],
            capture_output=True, text=True, check=True
        )
        
        output = result.stdout
        
        # Parse average complexity
        avg_match = re.search(r'Average complexity: ([0-9.]+)', output)
        if avg_match:
            complexity_data["average"] = float(avg_match.group(1))
        
        # Count functions with complexity > 10 (considered complex)
        complex_count = output.count(" C ")  # Radon marks complex functions with C
        complexity_data["complex_functions"] = complex_count
        
        # Find maximum complexity
        max_pattern = re.compile(r'- ([A-Z]) \(([0-9]+)\)')
        matches = max_pattern.findall(output)
        if matches:
            complexities = [int(m[1]) for m in matches]
            if complexities:
                complexity_data["max"] = max(complexities)
        
        # Run radon for maintainability index
        result = subprocess.run(
            ["radon", "mi", repo_dir, "-s"],
            capture_output=True, text=True, check=True
        )
        
        output = result.stdout
        
        # Parse average maintainability index
        mi_values = []
        for line in output.splitlines():
            if " - " in line:
                try:
                    mi_value = float(line.split(" - ")[1].strip())
                    mi_values.append(mi_value)
                except:
                    pass
        
        if mi_values:
            complexity_data["maintainability_index"] = sum(mi_values) / len(mi_values)
        
        # Run radon for Halstead metrics (if available)
        try:
            result = subprocess.run(
                ["radon", "hal", repo_dir],
                capture_output=True, text=True, check=True
            )
            
            output = result.stdout
            
            # Very basic parsing - would need more sophisticated parsing for real use
            volume_values = []
            difficulty_values = []
            effort_values = []
            
            for line in output.splitlines():
                if "h1:" in line and "h2:" in line:  # Line with Halstead metrics
                    parts = line.split()
                    for part in parts:
                        if part.startswith("volume:"):
                            try:
                                volume_values.append(float(part.split(":")[1]))
                            except:
                                pass
                        elif part.startswith("difficulty:"):
                            try:
                                difficulty_values.append(float(part.split(":")[1]))
                            except:
                                pass
                        elif part.startswith("effort:"):
                            try:
                                effort_values.append(float(part.split(":")[1]))
                            except:
                                pass
            
            if volume_values:
                complexity_data["halstead_metrics"]["volume"] = sum(volume_values) / len(volume_values)
            if difficulty_values:
                complexity_data["halstead_metrics"]["difficulty"] = sum(difficulty_values) / len(difficulty_values)
            if effort_values:
                complexity_data["halstead_metrics"]["effort"] = sum(effort_values) / len(effort_values)
        except:
            pass  # Halstead metrics might not be available
        
    except Exception as e:
        print(f"Error calculating complexity metrics: {e}")
    
    return complexity_data

def analyze_dependency_graph(repo_dir):
    """Analyze the dependency graph of the repository"""
    dependency_data = {
        "total_dependencies": 0,
        "direct_dependencies": 0,
        "dev_dependencies": 0,
        "outdated_dependencies": 0,
        "dependency_graph": {
            "nodes": 0,
            "edges": 0,
            "avg_degree": 0
        }
    }
    
    # Check for package.json (Node.js)
    package_json_path = os.path.join(repo_dir, "package.json")
    if os.path.exists(package_json_path):
        try:
            with open(package_json_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
            
            # Count dependencies
            dependencies = package_data.get("dependencies", {})
            dev_dependencies = package_data.get("devDependencies", {})
            
            dependency_data["direct_dependencies"] = len(dependencies)
            dependency_data["dev_dependencies"] = len(dev_dependencies)
            dependency_data["total_dependencies"] = len(dependencies) + len(dev_dependencies)
            
            # Check for package-lock.json or yarn.lock to get full dependency tree
            lock_file_path = os.path.join(repo_dir, "package-lock.json")
            if os.path.exists(lock_file_path):
                try:
                    with open(lock_file_path, 'r', encoding='utf-8') as f:
                        lock_data = json.load(f)
                    
                    if "dependencies" in lock_data:
                        all_deps = lock_data["dependencies"]
                        dependency_data["dependency_graph"]["nodes"] = len(all_deps)
                        
                        # Create a simple graph to count edges
                        G = nx.DiGraph()
                        for dep_name, dep_info in all_deps.items():
                            G.add_node(dep_name)
                            if "requires" in dep_info:
                                for req_name in dep_info["requires"]:
                                    G.add_edge(dep_name, req_name)
                        
                        dependency_data["dependency_graph"]["edges"] = G.number_of_edges()
                        
                        if G.number_of_nodes() > 0:
                            dependency_data["dependency_graph"]["avg_degree"] = G.number_of_edges() / G.number_of_nodes()
                except Exception as e:
                    print(f"Error analyzing package-lock.json: {e}")
        except Exception as e:
            print(f"Error analyzing package.json: {e}")
    
    # Check for requirements.txt (Python)
    requirements_path = os.path.join(repo_dir, "requirements.txt")
    if os.path.exists(requirements_path):
        try:
            with open(requirements_path, 'r', encoding='utf-8') as f:
                requirements = f.readlines()
            
            # Count direct dependencies
            direct_deps = [line.strip() for line in requirements if line.strip() and not line.startswith('#')]
            dependency_data["direct_dependencies"] = len(direct_deps)
            dependency_data["total_dependencies"] = len(direct_deps)
        except Exception as e:
            print(f"Error analyzing requirements.txt: {e}")
    
    return dependency_data

def check_test_coverage(repo_dir):
    """Try to determine test coverage"""
    coverage_data = {
        "has_tests": False, 
        "test_files": 0, 
        "test_to_code_ratio": 0,
        "test_lines": 0,
        "test_frameworks": []
    }
    
    # Look for test directories and files
    test_dirs = ['tests', 'test', '__tests__', 'spec', 'unit_tests', 'integration_tests', 'e2e']
    test_patterns = ['*_test.py', '*_spec.js', 'test_*.py', '*Test.java', '*Spec.js', '*_test.go', '*_test.rb']
    test_frameworks = {
        'pytest': r'import\s+pytest',
        'jest': r'import\s+.*\s+from\s+[\'"]@testing-library',
        'mocha': r'(describe|it)\s*\(',
        'junit': r'import\s+.*\s+from\s+[\'"]junit',
        'unittest': r'import\s+unittest',
        'rspec': r'RSpec\.',
        'go_test': r'func\s+Test\w+\('
    }
    
    test_files = []
    code_files = []
    test_lines_count = 0
    detected_frameworks = set()
    
    for root, dirs, files in os.walk(repo_dir):
        # Check if we're in a test directory
        in_test_dir = any(test_dir in root.split(os.path.sep) for test_dir in test_dirs)
        
        for file in files:
            file_path = os.path.join(root, file)
            
            # Skip non-code files
            if not any(file.endswith(ext) for ext in ['.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cs', '.go', '.rb', '.php']):
                continue
                
            # Check if it's a test file by directory or naming pattern
            is_test_file = in_test_dir or any(re.match(pattern.replace('*', '.*'), file) for pattern in test_patterns)
            
            if is_test_file:
                test_files.append(file_path)
                
                # Count test lines and detect frameworks
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        test_lines_count += len(content.split('\n'))
                        
                        # Detect test frameworks
                        for framework, pattern in test_frameworks.items():
                            if re.search(pattern, content):
                                detected_frameworks.add(framework)
                except Exception as e:
                    print(f"Error reading test file {file_path}: {e}")
            else:
                code_files.append(file_path)

    coverage_data["has_tests"] = len(test_files) > 0
    coverage_data["test_files"] = len(test_files)
    coverage_data["test_lines"] = test_lines_count
    coverage_data["test_frameworks"] = list(detected_frameworks)
    
    if len(code_files) > 0:
        coverage_data["test_to_code_ratio"] = len(test_files) / len(code_files)
    
    # Look for coverage configuration files
    coverage_files = [
        '.coveragerc',
        'coverage.xml',
        'coverage.json',
        'jest.config.js',
        'cypress.json',
        'codecov.yml',
        '.nycrc'
    ]
    
    coverage_data["has_coverage_config"] = any(
        os.path.exists(os.path.join(repo_dir, f)) for f in coverage_files
    )
    
    return coverage_data

def analyze_commit_history(repo_dir):
    """Analyze the commit history for patterns"""
    commit_data = {
        "total_commits": 0,
        "commit_frequency": 0,  # commits per week
        "active_days": 0,       # number of days with commits
        "contributors": 0,      # number of unique contributors
        "avg_commit_size": 0,   # average lines per commit
        "commit_message_quality": 0,  # score for commit message quality
        "test_driven_commits": 0  # commits that include test changes
    }
    
    try:
        # Get total commits count
        result = subprocess.run(
            ["git", "-C", repo_dir, "rev-list", "--count", "HEAD"],
            capture_output=True, text=True, check=True
        )
        commit_data["total_commits"] = int(result.stdout.strip())
        
        # Get commit dates for frequency
        result = subprocess.run(
            ["git", "-C", repo_dir, "log", "--format=%ad", "--date=short"],
            capture_output=True, text=True, check=True
        )
        commit_dates = result.stdout.strip().split('\n')
        unique_dates = set(commit_dates)
        commit_data["active_days"] = len(unique_dates)
        
        # Calculate commit frequency (commits per week)
        if commit_dates:
            try:
                first_date = datetime.strptime(commit_dates[-1], "%Y-%m-%d")
                last_date = datetime.strptime(commit_dates[0], "%Y-%m-%d")
                days_diff = (last_date - first_date).days + 1
                weeks = max(1, days_diff / 7)
                commit_data["commit_frequency"] = commit_data["total_commits"] / weeks
            except Exception as e:
                print(f"Error calculating commit frequency: {e}")
        
        # Get unique contributors
        result = subprocess.run(
            ["git", "-C", repo_dir, "log", "--format=%ae"],
            capture_output=True, text=True, check=True
        )
        commit_emails = result.stdout.strip().split('\n')
        commit_data["contributors"] = len(set(commit_emails))
        
        # Analyze commit message quality and test-driven commits
        result = subprocess.run(
            ["git", "-C", repo_dir, "log", "--format=%s", "--name-only"],
            capture_output=True, text=True, check=True
        )
        commit_logs = result.stdout.strip().split('\n\n')
        
        # Patterns for good commit messages
        good_message_patterns = [
            r'^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?:',  # Conventional commits
            r'^[A-Z]',  # Starts with capital letter
            r'.{10,}',  # At least 10 chars long
        ]
        
        # Count good commit messages and test-driven commits
        good_messages = 0
        test_commits = 0
        
        for i in range(0, len(commit_logs), 2):
            if i+1 < len(commit_logs):
                message = commit_logs[i]
                files = commit_logs[i+1].split('\n') if i+1 < len(commit_logs) else []
                
                # Check message quality
                if any(re.search(pattern, message) for pattern in good_message_patterns):
                    good_messages += 1
                
                # Check if commit includes test files
                if any('test' in f.lower() for f in files):
                    test_commits += 1
        
        # Calculate commit message quality score (0-1)
        if commit_data["total_commits"] > 0:
            commit_data["commit_message_quality"] = good_messages / commit_data["total_commits"]
            commit_data["test_driven_commits"] = test_commits
        
    except Exception as e:
        print(f"Error analyzing commit history: {e}")
    
    return commit_data

def analyze_repo_structure(repo_dir):
    """Analyze the repository structure"""
    structure = {
        "has_readme": False,
        "has_license": False,
        "has_gitignore": False,
        "has_ci_config": False,
        "has_dependency_manager": False,
        "has_docker": False,
        "has_contribution_guide": False,
        "has_code_of_conduct": False,
        "has_security_policy": False,
        "folder_depth": 0,
        "dependency_count": 0,
        "architecture_score": 0  # Score for architecture quality
    }
    
    # Check for key files
    structure["has_readme"] = any(
        os.path.exists(os.path.join(repo_dir, f)) for f in ["README.md", "README", "readme.md"]
    )
    structure["has_license"] = any(
        os.path.exists(os.path.join(repo_dir, f)) for f in ["LICENSE", "LICENSE.md", "license.txt"]
    )
    structure["has_gitignore"] = os.path.exists(os.path.join(repo_dir, ".gitignore"))
    structure["has_docker"] = any(
        os.path.exists(os.path.join(repo_dir, f)) for f in ["Dockerfile", "docker-compose.yml", ".dockerignore"]
    )
    structure["has_contribution_guide"] = any(
        os.path.exists(os.path.join(repo_dir, f)) for f in ["CONTRIBUTING.md", "CONTRIBUTE.md", ".github/CONTRIBUTING.md"]
    )
    structure["has_code_of_conduct"] = any(
        os.path.exists(os.path.join(repo_dir, f)) for f in ["CODE_OF_CONDUCT.md", ".github/CODE_OF_CONDUCT.md"]
    )
    structure["has_security_policy"] = any(
        os.path.exists(os.path.join(repo_dir, f)) for f in ["SECURITY.md", ".github/SECURITY.md", "security.md"]
    )
    
    # Check for CI configuration files
    ci_files = ['.travis.yml', '.github/workflows', 'circleci', 'jenkinsfile']
    structure["has_ci_config"] = any(
        os.path.exists(os.path.join(repo_dir, f)) if os.path.isfile(os.path.join(repo_dir, f))
        else os.path.isdir(os.path.join(repo_dir, f))
        for f in ci_files
    )
    
    # Check for dependency manager configuration
    structure["has_dependency_manager"] = any(
        os.path.exists(os.path.join(repo_dir, f)) for f in ["package.json", "requirements.txt", "Gemfile", "composer.json"]
    )
    
    # Calculate folder depth (max depth)
    max_depth = 0
    for root, dirs, files in os.walk(repo_dir):
        depth = root[len(repo_dir):].count(os.sep)
        if depth > max_depth:
            max_depth = depth
    structure["folder_depth"] = max_depth
    
    # Count dependency files (as a simple dependency count)
    dep_files = [f for f in os.listdir(repo_dir) if f in ["package.json", "requirements.txt", "Gemfile", "composer.json"]]
    structure["dependency_count"] = len(dep_files)
    
    # Calculate a simple architecture score based on the presence of key files (normalized to 0-1)
    score = 0
    if structure["has_readme"]:
        score += 1
    if structure["has_license"]:
        score += 1
    if structure["has_gitignore"]:
        score += 1
    if structure["has_ci_config"]:
        score += 1
    if structure["has_dependency_manager"]:
        score += 1
    if structure["has_docker"]:
        score += 1
    if structure["has_contribution_guide"]:
        score += 1
    if structure["has_code_of_conduct"]:
        score += 1
    if structure["has_security_policy"]:
        score += 1
    structure["architecture_score"] = score / 9.0
    
    return structure

def read_repo_links(csv_path):
    """Read repository links from a CSV file with structure: country,org/group,repo_link"""
    repos = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip the header
            for row in reader:
                if len(row) >= 3:  # Ensure we have country, org/group, and repo_link
                    repos.append({
                        'country': row[0],
                        'org': row[1],
                        'repo_link': row[2]
                    })
    except Exception as e:
        print(f"Error reading CSV file: {e}")
    return repos

def derive_gemini_scores(repo_dir, files):
    """
    Use the Gemini 2.0 Flash model to analyze repository code and derive additional sustainability scores.
    This function aggregates code samples (up to a maximum total character limit) and sends them
    as context to the model. The model is then prompted to provide scores (0-100) on various dimensions.
    """
    code_samples = []
    max_total_chars = 500000  # Set a limit to avoid huge payloads (adjust as needed)
    total_chars = 0
    for file in files:
        try:
            with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()
            if total_chars + len(code) < max_total_chars:
                code_samples.append(f"File: {file}\n{code}\n")
                total_chars += len(code)
            else:
                # Stop adding if we've reached our maximum length
                break
        except Exception as e:
            print(f"Error reading file {file}: {e}")
    
    aggregated_code = "\n".join(code_samples)
    
    prompt = f"""
You are an expert code sustainability evaluator. Given the repository code samples, provide an evaluation with numerical scores (0-100) for the following metrics:

Please respond ONLY with a JSON object with the following structure and no other text:
{{
  "overall_sustainability": [score],
  "documentation_quality": [score],
  "testing_robustness": [score],
  "modularity_and_design": [score],
  "error_handling": [score],
  "security_best_practices": [score],
  "scalability_potential": [score],
  "environmental_efficiency": [score],
  "social_inclusiveness": [score],
  "critical_issues": ["issue1", "issue2", ...],
  "improvement_suggestions": ["suggestion1", "suggestion2", ...]
}}

Repository code:
{aggregated_code}
"""
    try:
        # Call Gemini 2.0 Flash model (which supports a large context window)
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        # Attempt to parse the response as JSON for structured output
        try:
            #print(f"Gemini response: {response.text}")
            gemini_scores = json.loads(response.text)
        except Exception as parse_error:
            print(f"Error parsing Gemini response as JSON: {parse_error}")
            # Try to extract JSON from the response text
            print("Attempting to extract JSON from response text")
            text = response.text
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                try:
                    json_str = text[json_start:json_end]
                    gemini_scores = json.loads(json_str)
                    print("Extracted JSON successfully")
                except:
                    gemini_scores = {"raw_response": text}
            else:
                gemini_scores = {"raw_response": text}
    except Exception as e:
        print(f"Error calling Gemini model: {e}")
        gemini_scores = {"error": str(e)}
    
    return gemini_scores

def analyze_repository(repo_url, target_dir):
    """
    High-level function to analyze a repository.
    It clones the repository, gathers all code files, and then computes:
      - Code patterns and metrics
      - Cyclomatic complexity
      - Dependency graph analysis
      - Test coverage
      - Commit history
      - Repository structure
      - Gemini-based sustainability scores
    """
    if clone_repo(repo_url, target_dir):
        files = get_code_files(target_dir)
        
        # Check if there are any code files
        if not files:
            print(f"No code files found in repository: {repo_url}")
            return None
        
        code_analysis = analyze_code_patterns(files)
        complexity_analysis = calculate_cyclomatic_complexity(target_dir)
        dependency_analysis = analyze_dependency_graph(target_dir)
        test_coverage = check_test_coverage(target_dir)
        commit_history = analyze_commit_history(target_dir)
        repo_structure = analyze_repo_structure(target_dir)
        gemini_scores = derive_gemini_scores(target_dir, files)
        
        overall_analysis = {
            "code_analysis": code_analysis,
            "complexity_analysis": complexity_analysis,
            "dependency_analysis": dependency_analysis,
            "test_coverage": test_coverage,
            "commit_history": commit_history,
            "repo_structure": repo_structure,
            "gemini_scores": gemini_scores
        }
        
        return overall_analysis
    else:
        return None

if __name__ == "__main__":
    csv_path = "repo_links.csv"
    output_dir = "analysis_results"
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Read repositories from CSV
    repos = read_repo_links(csv_path)
    print(f"Found {len(repos)} repositories in CSV")
    
    # Process each repository
    results = []
    country_repo_count = Counter()
    
    for i, repo_info in enumerate(repos):
        country = repo_info['country']
        
        if country_repo_count[country] >= 30:
            continue
        
        print(f"Processing repository {i+1}/{len(repos)}: {repo_info['repo_link']}")
        
        # Create a unique temporary directory for each repository
        with tempfile.TemporaryDirectory() as tmp_dir:
            target_dir = os.path.join(tmp_dir, "repo")
            print(f"Cloning repository to {target_dir}")
            
            # Analyze the repository
            analysis = analyze_repository(repo_info['repo_link'], target_dir)
            
            if analysis:
                # Add metadata from CSV
                analysis['metadata'] = {
                    'country': repo_info['country'],
                    'org': repo_info['org'],
                    'repo_link': repo_info['repo_link']
                }
                
                # Save individual result
                repo_name = repo_info['repo_link'].split('/')[-1].replace('.git', '')
                file_name = f"{repo_info['country']}_{repo_name}.json"
                file_path = os.path.join(output_dir, file_name)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(analysis, f, indent=2)
                
                print(f"Analysis for {repo_info['repo_link']} saved to {file_path}")
                
                # Add to results collection
                results.append(analysis)
                country_repo_count[country] += 1
            else:
                print(f"Failed to analyze repository: {repo_info['repo_link']}")
    
    # Save combined results
    combined_file_path = os.path.join(output_dir, "all_results.json")
    with open(combined_file_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"All analyses completed. Combined results saved to {combined_file_path}")
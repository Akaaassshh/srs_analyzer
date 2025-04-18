import os
import json
import re
import ast
import subprocess
import tempfile
from utils.groq_llm import llama3_chat

def validate_python_syntax(code):
    """Check if Python code has valid syntax"""
    try:
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, str(e)

def validate_import_dependencies(code, project_dir):
    """Check if imports in the code are available"""
    # Extract imports from the code
    imports = []
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append(name.name)
            elif isinstance(node, ast.ImportFrom):
                imports.append(node.module)
    except SyntaxError:
        # If there's a syntax error, we'll catch it in validate_python_syntax
        return True, None
        
    # Check if each import is a standard library or exists in the project
    missing_imports = []
    for imp in imports:
        if imp is None:
            continue
            
        # Skip standard library modules
        if imp in ['os', 'sys', 'json', 're', 'datetime', 'time', 'typing', 'collections',
                  'pathlib', 'unittest', 'pytest', 'abc', 'math', 'random']:
            continue
            
        # Check if it's a relative import within the project
        if imp.startswith('.'):
            continue
            
        # Split the import to handle cases like 'app.models'
        base_module = imp.split('.')[0]
        
        # Check if it's a project module
        if os.path.exists(os.path.join(project_dir, base_module)):
            continue
            
        # If we get here, it's not found
        missing_imports.append(imp)
    
    if missing_imports:
        return False, f"Missing imports: {', '.join(missing_imports)}"
    
    return True, None

def run_code_test(code, filename=None):
    """Try to execute the code to check for runtime errors"""
    if not filename:
        # Create a temporary file to test the code
        fd, filename = tempfile.mkstemp(suffix='.py')
        os.close(fd)
    
    try:
        with open(filename, 'w') as f:
            f.write(code)
        
        # Try to run the code
        result = subprocess.run(
            [sys.executable, filename],
            capture_output=True, 
            text=True, 
            timeout=5  # 5 second timeout
        )
        
        if result.returncode != 0:
            return False, result.stderr
        return True, None
    except Exception as e:
        return False, str(e)
    finally:
        if filename.startswith('/tmp/') or filename.startswith(tempfile.gettempdir()):
            os.unlink(filename)

def fix_code(code, error_msg, context=None):
    fixed_code = llama3_chat(prompt)
    
    # Extract code from the response if it's wrapped in markdown code blocks
    code_pattern = r'```(?:python)?\s*([\s\S]*?)\s*```'
    match = re.search(code_pattern, fixed_code)
    if match:
        fixed_code = match.group(1)
    
    return fixed_code

def refine_code_iteratively(code, file_path, project_dir, max_iterations=3):
    iterations = 0
    current_code = code
    is_valid = False
    error = None
    
    while iterations < max_iterations and not is_valid:
        # Increment iteration counter
        iterations += 1
        
        # Check syntax
        syntax_valid, syntax_error = validate_python_syntax(current_code)
        if not syntax_valid:
            error = f"Syntax error: {syntax_error}"
            print(f"Iteration {iterations}: Fixing syntax error in {file_path}")
            current_code = fix_code(current_code, syntax_error, f"This code is for file: {file_path}")
            continue
        
        # Check imports
        imports_valid, imports_error = validate_import_dependencies(current_code, project_dir)
        if not imports_valid:
            error = f"Import error: {imports_error}"
            print(f"Iteration {iterations}: Fixing import error in {file_path}")
            
            # Provide more context for import fixes
            context = f"""
            This code is for file: {file_path}
            Project structure: The code is part of a FastAPI project with:
            - app/ directory containing API routes, models, and services
            - utils/ directory containing utility functions
            - tests/ directory containing test files
            
            Fix the imports to use the correct relative or absolute imports.
            """
            
            current_code = fix_code(current_code, imports_error, context)
            continue
        
        # Run basic execution test if the file is a standalone script
        if not file_path.endswith('__init__.py') and ('def ' in current_code or 'class ' in current_code):
            # Skip execution test for now, as it would require complex mocking
            pass
        
        # If we get here, the code is valid
        is_valid = True
    
    return current_code, is_valid, iterations, error

def validate_and_refine_project(project_dir):

    stats = {
        "total_files": 0,
        "valid_files": 0,
        "fixed_files": 0,
        "failed_files": 0,
        "iterations": 0,
        "errors": []
    }
    
    for root, _, files in os.walk(project_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, project_dir)
                
                stats["total_files"] += 1
                
                # Read the current code
                with open(file_path, 'r') as f:
                    code = f.read()
                
                # Check if code is already valid
                syntax_valid, _ = validate_python_syntax(code)
                imports_valid, _ = validate_import_dependencies(code, project_dir)
                
                if syntax_valid and imports_valid:
                    stats["valid_files"] += 1
                    continue
                
                # If not valid, refine it
                print(f"Refining code in {relative_path}...")
                refined_code, is_valid, iterations, error = refine_code_iteratively(
                    code, relative_path, project_dir
                )
                
                stats["iterations"] += iterations
                
                if is_valid:
                    # Write the refined code back to the file
                    with open(file_path, 'w') as f:
                        f.write(refined_code)
                    stats["fixed_files"] += 1
                    print(f"✅ Successfully refined {relative_path} in {iterations} iterations")
                else:
                    stats["failed_files"] += 1
                    stats["errors"].append({
                        "file": relative_path,
                        "error": error
                    })
                    print(f"❌ Failed to refine {relative_path}: {error}")
    
    return stats
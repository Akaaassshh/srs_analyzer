import os
import json
import subprocess
import sys
from pathlib import Path

def generate_project_structure(structure_json: dict, output_dir: str = None):
    try:
        # Parse the JSON string
        print("==========================================================")
        print(structure_json)
        structure = json.loads(structure_json)
       
        # Default to generating in the srs_analyzer directory
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "generated_project")
        
        # Create base directory
        base_dir = Path(output_dir)
        base_dir.mkdir(exist_ok=True, parents=True)
        
        # Process the structure recursively
        process_structure(structure, base_dir)
        
        # Make setup.sh executable if it exists
        setup_file = base_dir / "setup.sh"
        if setup_file.exists():
            make_executable(str(setup_file))
        
        # For Windows, also create a setup.bat file
        if os.name == 'nt' and not (base_dir / "setup.bat").exists() and setup_file.exists():
            create_windows_batch_file(setup_file, base_dir / "setup.bat")
        
        print(f"✅ Project structure generated successfully in {output_dir}")
        return True, f"Project created in {output_dir}"
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON: {str(e)}")
        return False, f"Failed to parse JSON: {str(e)}"
    except Exception as e:
        print(f"❌ Error generating project structure: {str(e)}")
        return False, f"Error generating project structure: {str(e)}"

def create_windows_batch_file(setup_sh_path, batch_file_path):
    """Create a Windows batch file equivalent of the setup.sh script"""
    try:
        # Read the setup.sh file
        with open(setup_sh_path, 'r', encoding='utf-8') as f:
            bash_content = f.read()
            
        # Simple conversion of common bash commands to Windows commands
        # This is a basic conversion and may not handle all cases
        batch_content = "@echo off\n"
        batch_content += ":: Generated from setup.sh\n"
        batch_content += ":: Note: This is a simple conversion and may not be complete\n\n"
        
        # Convert bash lines to batch commands
        for line in bash_content.splitlines():
            line = line.strip()
            # Skip comments
            if line.startswith("#"):
                batch_content += f":: {line[1:]}\n"
                continue
                
            # Skip empty lines
            if not line:
                batch_content += "\n"
                continue
                
            # Simple conversions
            if "pip install" in line:
                batch_content += f"{line}\n"
            elif line.startswith("mkdir"):
                batch_content += f"{line}\n"
            elif line.startswith("cd"):
                batch_content += f"{line}\n"
            elif line.startswith("python"):
                batch_content += f"{line}\n"
            else:
                batch_content += f":: NEEDS MANUAL CONVERSION: {line}\n"
        
        # Add pause at the end
        batch_content += "\npause\n"
        
        with open(batch_file_path, 'w', encoding='utf-8') as f:
            f.write(batch_content)
            
        print(f"✅ Created Windows batch file: {batch_file_path}")
    except Exception as e:
        print(f"❌ Failed to create Windows batch file: {str(e)}")

def process_structure(structure, parent_dir):
    """
    Recursively process the structure and create files/directories
    """
    for key, value in structure.items():
        path = parent_dir / key
        
        # If key ends with /, it's a directory
        if key.endswith('/'):
            path.mkdir(exist_ok=True)
            # Process contents of this directory
            if isinstance(value, dict):
                process_structure(value, path)
        else:
            # It's a file
            # Ensure parent directory exists
            path.parent.mkdir(exist_ok=True, parents=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(str(value))
                
            # If it's a Python file, fix line endings for Windows
            if path.suffix == '.py' and os.name == 'nt':
                fix_line_endings(path)

def fix_line_endings(file_path):
    """Fix line endings in text files for Windows"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ensure Windows line endings
        content = content.replace('\r\n', '\n').replace('\n', '\r\n')
        
        with open(file_path, 'w', encoding='utf-8', newline='\r\n') as f:
            f.write(content)
    except Exception:
        # Silently fail if we can't fix line endings
        pass

def make_executable(path):
    """Make a file executable"""
    if os.name != 'nt':  # Skip on Windows as it doesn't use file permissions in the same way
        mode = os.stat(path).st_mode
        os.chmod(path, mode | 0o111)

def setup_virtual_env(project_dir):
    """
    Create and set up a virtual environment for the project
    """
    try:
        venv_path = os.path.join(project_dir, "venv")
        
        # Create virtual environment
        subprocess.check_call([sys.executable, "-m", "venv", venv_path])
        
        # Determine the pip and activate script paths based on OS
        if os.name == 'nt':  # Windows
            pip_path = os.path.join(venv_path, "Scripts", "pip.exe")
            activate_path = os.path.join(venv_path, "Scripts", "activate.bat")
        else:  # Unix/Linux/Mac
            pip_path = os.path.join(venv_path, "bin", "pip")
            activate_path = os.path.join(venv_path, "bin", "activate")
        
        # Install requirements if they exist
        req_file = os.path.join(project_dir, "requirements.txt")
        if os.path.exists(req_file):
            try:
                subprocess.check_call([pip_path, "install", "-r", req_file])
            except subprocess.CalledProcessError:
                # Fallback approach if direct pip call fails
                if os.name == 'nt':
                    activate_cmd = f"{activate_path} && pip install -r {req_file}"
                    subprocess.check_call(activate_cmd, shell=True)
                else:
                    activate_cmd = f"source {activate_path} && pip install -r {req_file}"
                    subprocess.check_call(activate_cmd, shell=True, executable='/bin/bash')
            
        print(f"✅ Virtual environment set up at {venv_path}")
        print(f"To activate: {activate_path}")
        return True, f"Virtual environment set up at {venv_path}"
    except Exception as e:
        print(f"❌ Error setting up virtual environment: {str(e)}")
        return False, f"Error setting up virtual environment: {str(e)}"
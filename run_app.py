#!/usr/bin/env python3
"""
StudyMate Application Launcher
Simple launcher to start the StudyMate application
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Launch the StudyMate application"""
    print("🚀 Starting StudyMate Application...")
    print("=" * 50)
    
    # Get the current directory
    app_dir = Path(__file__).parent
    os.chdir(app_dir)
    
    # Check if virtual environment exists
    venv_path = app_dir / "venv"
    if venv_path.exists():
        print("✅ Virtual environment found")
        
        # Use the virtual environment's Python
        if os.name == 'nt':  # Windows
            python_exe = venv_path / "Scripts" / "python.exe"
            streamlit_exe = venv_path / "Scripts" / "streamlit.exe"
        else:  # Unix/Linux/Mac
            python_exe = venv_path / "bin" / "python"
            streamlit_exe = venv_path / "bin" / "streamlit"
        
        if python_exe.exists() and streamlit_exe.exists():
            print(f"✅ Using Python: {python_exe}")
            print(f"✅ Using Streamlit: {streamlit_exe}")
            
            # Run the application
            cmd = [str(streamlit_exe), "run", "main.py", "--server.port", "8505"]
            print(f"🔄 Running command: {' '.join(cmd)}")
            
            try:
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError as e:
                print(f"❌ Error running application: {e}")
                return False
            except KeyboardInterrupt:
                print("\n👋 Application stopped by user")
                return True
        else:
            print("❌ Python or Streamlit not found in virtual environment")
            return False
    else:
        print("⚠️  No virtual environment found, using system Python")
        
        # Use system Python
        try:
            cmd = ["streamlit", "run", "main.py", "--server.port", "8505"]
            print(f"🔄 Running command: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error running application: {e}")
            return False
        except KeyboardInterrupt:
            print("\n👋 Application stopped by user")
            return True
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Failed to start StudyMate application")
        sys.exit(1)
    else:
        print("\n✅ StudyMate application finished successfully")
        sys.exit(0)

#!/usr/bin/env python3
"""
StudyMate Setup Script
Automated setup for StudyMate with HuggingFace integration
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_banner():
    """Print StudyMate banner"""
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   📚 StudyMate - AI Academic Assistant Setup                 ║
    ║                                                               ║
    ║   🤖 HuggingFace Integration (IBM Granite + Mistral)         ║
    ║   🔍 FAISS Vector Database                                    ║
    ║   📄 PyMuPDF Processing                                       ║
    ║   🎨 Modern Streamlit Interface                               ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
    return True

def create_virtual_environment():
    """Create virtual environment"""
    print("\n🔧 Creating virtual environment...")
    
    venv_path = Path("venv")
    if venv_path.exists():
        print("   Virtual environment already exists")
        return True
    
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to create virtual environment")
        return False

def get_pip_command():
    """Get the correct pip command for the platform"""
    if platform.system() == "Windows":
        return str(Path("venv") / "Scripts" / "pip.exe")
    else:
        return str(Path("venv") / "bin" / "pip")

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    
    pip_cmd = get_pip_command()
    requirements_file = "requirements_production.txt"
    
    if not Path(requirements_file).exists():
        print(f"❌ Requirements file {requirements_file} not found")
        return False
    
    try:
        # Upgrade pip first
        subprocess.run([pip_cmd, "install", "--upgrade", "pip"], check=True)
        
        # Install requirements
        subprocess.run([pip_cmd, "install", "-r", requirements_file], check=True)
        
        # Install sentence-transformers separately
        subprocess.run([pip_cmd, "install", "sentence-transformers"], check=True)
        
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_environment():
    """Setup environment configuration"""
    print("\n⚙️ Setting up environment configuration...")
    
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if not env_example.exists():
        print("❌ .env.example file not found")
        return False
    
    if env_file.exists():
        print("   .env file already exists")
        return True
    
    try:
        # Copy .env.example to .env
        with open(env_example, 'r') as src, open(env_file, 'w') as dst:
            dst.write(src.read())
        
        print("✅ Environment file created (.env)")
        print("   📝 Please edit .env file with your HuggingFace token")
        print("   🔗 Get token from: https://huggingface.co/settings/tokens")
        return True
    except Exception as e:
        print(f"❌ Failed to create environment file: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = [
        "data/uploads",
        "data/processed", 
        "data/embeddings",
        "logs",
        "temp"
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        
        # Create .gitkeep files
        gitkeep = Path(dir_path) / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.touch()
    
    print("✅ Directories created successfully")
    return True

def print_next_steps():
    """Print next steps for the user"""
    print("""
    🎉 StudyMate Setup Complete!
    
    📋 Next Steps:
    
    1. 🔑 Configure HuggingFace Token:
       - Edit the .env file
       - Add your HuggingFace token
       - Get token from: https://huggingface.co/settings/tokens
    
    2. 🚀 Run StudyMate:
       - Windows: venv\\Scripts\\activate && streamlit run app.py
       - Linux/Mac: source venv/bin/activate && streamlit run app.py
    
    3. 🌐 Open Browser:
       - Navigate to: http://localhost:8502
    
    4. 📚 Start Using:
       - Upload PDF documents
       - Choose AI model (IBM Granite or Mistral)
       - Ask questions about your documents
    
    💡 Tips:
    - First run will download models (~3-7GB)
    - GPU recommended for faster inference
    - 8GB+ RAM recommended
    
    🆘 Need Help?
    - Check README.md for detailed instructions
    - Visit GitHub issues for support
    
    Happy studying! 📖✨
    """)

def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_environment():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        sys.exit(1)
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main()

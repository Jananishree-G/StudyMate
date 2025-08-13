#!/usr/bin/env python3
"""
Environment setup script for StudyMate
This script helps you configure the required environment variables
"""

import os
import sys
from pathlib import Path

def print_header():
    """Print welcome header"""
    print("=" * 60)
    print("🎓 StudyMate Environment Setup")
    print("=" * 60)
    print()

def check_env_file():
    """Check if .env file exists"""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        print("Creating .env file from template...")
        
        # Copy from .env.example
        example_file = Path(".env.example")
        if example_file.exists():
            with open(example_file, 'r') as f:
                content = f.read()
            
            with open(env_file, 'w') as f:
                f.write(content)
            
            print("✅ Created .env file from template")
        else:
            print("❌ .env.example file not found!")
            return False
    
    return True

def get_user_input(prompt, default="", required=True):
    """Get user input with validation"""
    while True:
        if default:
            user_input = input(f"{prompt} [{default}]: ").strip()
            if not user_input:
                user_input = default
        else:
            user_input = input(f"{prompt}: ").strip()
        
        if user_input or not required:
            return user_input
        
        if required:
            print("❌ This field is required. Please enter a value.")

def setup_watson_credentials():
    """Setup IBM Watson credentials"""
    print("\n🤖 IBM Watson Configuration")
    print("-" * 30)
    print("You need to get these credentials from IBM Cloud:")
    print("1. Go to https://cloud.ibm.com/")
    print("2. Create or access Watson Machine Learning service")
    print("3. Get your API key and Project ID")
    print()
    
    api_key = get_user_input("Enter your Watson API Key", required=True)
    project_id = get_user_input("Enter your Watson Project ID", required=True)
    url = get_user_input("Enter Watson URL", "https://us-south.ml.cloud.ibm.com", required=False)
    
    return {
        'WATSONX_API_KEY': api_key,
        'WATSONX_PROJECT_ID': project_id,
        'WATSONX_URL': url
    }

def setup_huggingface_credentials():
    """Setup HuggingFace credentials (optional)"""
    print("\n🤗 HuggingFace Configuration (Optional)")
    print("-" * 40)
    print("HuggingFace API key is optional but recommended for better performance.")
    print("Get it from: https://huggingface.co/settings/tokens")
    print()
    
    use_hf = input("Do you want to configure HuggingFace? (y/n) [n]: ").strip().lower()
    
    if use_hf in ['y', 'yes']:
        api_key = get_user_input("Enter your HuggingFace API Key", required=False)
        return {'HUGGINGFACE_API_KEY': api_key} if api_key else {}
    
    return {}

def update_env_file(credentials):
    """Update .env file with new credentials"""
    env_file = Path(".env")
    
    # Read current content
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Update lines with new credentials
    updated_lines = []
    for line in lines:
        updated = False
        for key, value in credentials.items():
            if line.startswith(f"{key}="):
                updated_lines.append(f"{key}={value}\n")
                updated = True
                break
        
        if not updated:
            updated_lines.append(line)
    
    # Write updated content
    with open(env_file, 'w') as f:
        f.writelines(updated_lines)

def verify_setup():
    """Verify the setup by loading environment variables"""
    print("\n🔍 Verifying Setup...")
    print("-" * 20)
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        # Check required variables
        required_vars = ['WATSONX_API_KEY', 'WATSONX_PROJECT_ID']
        missing_vars = []
        
        for var in required_vars:
            value = os.getenv(var)
            if not value or value == f"your_{var.lower()}_here":
                missing_vars.append(var)
            else:
                print(f"✅ {var}: {'*' * (len(value) - 4) + value[-4:]}")
        
        if missing_vars:
            print(f"\n❌ Missing required variables: {', '.join(missing_vars)}")
            return False
        
        # Check optional variables
        optional_vars = ['HUGGINGFACE_API_KEY']
        for var in optional_vars:
            value = os.getenv(var)
            if value and value != f"your_{var.lower()}_here":
                print(f"✅ {var}: {'*' * (len(value) - 4) + value[-4:]}")
            else:
                print(f"⚠️  {var}: Not configured (optional)")
        
        return True
        
    except ImportError:
        print("❌ python-dotenv not installed. Run: pip install python-dotenv")
        return False
    except Exception as e:
        print(f"❌ Error verifying setup: {e}")
        return False

def test_connection():
    """Test connection to APIs"""
    print("\n🧪 Testing API Connections...")
    print("-" * 30)
    
    try:
        # Test Watson connection
        print("Testing Watson connection...")
        # Note: Actual connection test would require the full setup
        print("⚠️  Connection test requires full application setup")
        print("   Run 'streamlit run main.py' to test the full application")
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")

def print_next_steps():
    """Print next steps"""
    print("\n🎉 Setup Complete!")
    print("-" * 20)
    print("Next steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Run the application: streamlit run main.py")
    print("3. Open your browser to http://localhost:8501")
    print("4. Upload PDF documents and start asking questions!")
    print()
    print("📚 For more help, check:")
    print("   - docs/installation.md")
    print("   - docs/usage.md")
    print("   - README.md")

def main():
    """Main setup function"""
    print_header()
    
    # Check if .env file exists
    if not check_env_file():
        sys.exit(1)
    
    # Collect credentials
    all_credentials = {}
    
    # Watson credentials (required)
    watson_creds = setup_watson_credentials()
    all_credentials.update(watson_creds)
    
    # HuggingFace credentials (optional)
    hf_creds = setup_huggingface_credentials()
    all_credentials.update(hf_creds)
    
    # Update .env file
    print("\n💾 Updating .env file...")
    update_env_file(all_credentials)
    print("✅ Environment file updated")
    
    # Verify setup
    if verify_setup():
        print("\n✅ All required credentials configured!")
    else:
        print("\n❌ Setup incomplete. Please check the missing credentials.")
        return
    
    # Test connections
    test_connection()
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main()

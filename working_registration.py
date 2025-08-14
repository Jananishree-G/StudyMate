#!/usr/bin/env python3
"""
Working Registration Solution
Simple command-line registration that definitely works
"""

import requests
import json
from datetime import datetime

API_BASE_URL = "http://localhost:8000"

def test_backend():
    """Test backend connection"""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False

def register_user():
    """Interactive user registration"""
    print("=" * 60)
    print("STUDYMATE USER REGISTRATION")
    print("=" * 60)
    
    # Check backend
    if not test_backend():
        print("ERROR: Backend API is not running!")
        print("Please start the backend with: python backend_api.py")
        return False
    
    print("Backend API is connected. Let's create your account!\n")
    
    # Get user input
    username = input("Enter username: ").strip()
    email = input("Enter email: ").strip()
    full_name = input("Enter full name (optional): ").strip()
    password = input("Enter password (6+ characters): ").strip()
    
    # Validate
    if not username:
        print("ERROR: Username is required!")
        return False
    
    if not email:
        print("ERROR: Email is required!")
        return False
    
    if not password:
        print("ERROR: Password is required!")
        return False
    
    if len(password) < 6:
        print("ERROR: Password must be at least 6 characters!")
        return False
    
    # Register
    user_data = {
        "username": username,
        "email": email,
        "password": password,
        "full_name": full_name
    }
    
    print(f"\nRegistering user: {username}...")
    
    try:
        response = requests.post(f"{API_BASE_URL}/auth/register",
                               json=user_data,
                               headers={'Content-Type': 'application/json'},
                               timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("\n" + "=" * 60)
            print("SUCCESS: ACCOUNT CREATED!")
            print("=" * 60)
            print(f"Username: {result['user']['username']}")
            print(f"Email: {result['user']['email']}")
            print(f"Full Name: {result['user'].get('full_name', 'Not provided')}")
            print(f"User ID: {result['user']['id']}")
            print(f"Created: {result['user']['created_at']}")
            print(f"Token: {result['access_token'][:20]}...")
            
            # Test login
            print("\nTesting login with new account...")
            login_response = requests.post(f"{API_BASE_URL}/auth/login",
                                         json={"username": username, "password": password},
                                         timeout=10)
            
            if login_response.status_code == 200:
                print("SUCCESS: Login test passed!")
                print("\nYour account is ready to use!")
                print(f"Login credentials:")
                print(f"  Username: {username}")
                print(f"  Password: {password}")
                return True
            else:
                print("WARNING: Registration succeeded but login test failed")
                return True
                
        else:
            error = response.json()
            print(f"\nERROR: Registration failed!")
            print(f"Reason: {error.get('detail', 'Unknown error')}")
            
            if "already registered" in str(error).lower():
                print("SUGGESTION: Try a different username or email")
            
            return False
            
    except Exception as e:
        print(f"\nERROR: Connection failed - {e}")
        return False

def create_test_account():
    """Create a test account automatically"""
    timestamp = str(int(datetime.now().timestamp()))
    test_user = {
        "username": f"quicktest_{timestamp}",
        "email": f"quicktest_{timestamp}@studymate.com",
        "password": "quicktest123",
        "full_name": "Quick Test User"
    }
    
    print("Creating quick test account...")
    print(f"Username: {test_user['username']}")
    print(f"Password: {test_user['password']}")
    
    try:
        response = requests.post(f"{API_BASE_URL}/auth/register",
                               json=test_user,
                               headers={'Content-Type': 'application/json'},
                               timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("\nSUCCESS: Quick test account created!")
            print(f"Login with:")
            print(f"  Username: {test_user['username']}")
            print(f"  Password: {test_user['password']}")
            return test_user
        else:
            print("ERROR: Quick test account creation failed")
            return None
            
    except Exception as e:
        print(f"ERROR: {e}")
        return None

def main():
    print("STUDYMATE REGISTRATION SOLUTION")
    print("=" * 60)
    print("Choose an option:")
    print("1. Create your own account (interactive)")
    print("2. Create quick test account (automatic)")
    print("3. Exit")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        success = register_user()
        if success:
            print("\n" + "=" * 60)
            print("REGISTRATION COMPLETE!")
            print("You can now login to StudyMate at:")
            print("  Flask App: http://localhost:8506")
            print("  Streamlit App: http://localhost:8507")
            print("=" * 60)
    
    elif choice == "2":
        test_account = create_test_account()
        if test_account:
            print("\n" + "=" * 60)
            print("QUICK TEST ACCOUNT READY!")
            print("Use these credentials to login:")
            print(f"  Username: {test_account['username']}")
            print(f"  Password: {test_account['password']}")
            print("\nLogin at:")
            print("  Flask App: http://localhost:8506")
            print("  Streamlit App: http://localhost:8507")
            print("=" * 60)
    
    elif choice == "3":
        print("Goodbye!")
    
    else:
        print("Invalid choice!")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Create User Account - Easy way to create a new StudyMate account
"""

import requests
import json

API_BASE_URL = "http://localhost:8000"

def create_account():
    """Interactive account creation"""
    print("=" * 60)
    print("CREATE NEW STUDYMATE ACCOUNT")
    print("=" * 60)
    
    # Check API connection
    try:
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code != 200:
            print("ERROR: Backend API is not running!")
            print("Please start the backend with: python backend_api.py")
            return
    except:
        print("ERROR: Cannot connect to backend API!")
        print("Please start the backend with: python backend_api.py")
        return
    
    print("Backend API is running. Let's create your account!\n")
    
    # Get user input
    print("Please provide the following information:")
    username = input("Username: ").strip()
    email = input("Email: ").strip()
    full_name = input("Full Name (optional): ").strip()
    password = input("Password (6+ characters): ").strip()
    confirm_password = input("Confirm Password: ").strip()
    
    # Validate input
    if not username:
        print("ERROR: Username is required!")
        return
    
    if not email:
        print("ERROR: Email is required!")
        return
    
    if not password:
        print("ERROR: Password is required!")
        return
    
    if len(password) < 6:
        print("ERROR: Password must be at least 6 characters!")
        return
    
    if password != confirm_password:
        print("ERROR: Passwords do not match!")
        return
    
    # Create account
    user_data = {
        "username": username,
        "email": email,
        "password": password,
        "full_name": full_name if full_name else ""
    }
    
    print("\nCreating account...")
    
    try:
        response = requests.post(f"{API_BASE_URL}/auth/register", json=user_data)
        
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
            print("\nYour account has been created successfully!")
            print("You can now login to StudyMate with these credentials:")
            print(f"Username: {username}")
            print(f"Password: {password}")
            print("\nAccess StudyMate at: http://localhost:8504")
            
        else:
            error = response.json()
            print(f"\nERROR: Account creation failed!")
            print(f"Reason: {error.get('detail', 'Unknown error')}")
            
            if "already registered" in str(error).lower():
                print("\nSUGGESTION: Try a different username or email address")
            
    except Exception as e:
        print(f"\nERROR: Connection failed - {e}")

def main():
    create_account()
    
    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print("1. Open StudyMate: http://localhost:8504")
    print("2. Click 'Login' tab")
    print("3. Enter your username and password")
    print("4. Start uploading PDFs and chatting with AI!")
    print("\nIf you have any issues, run: python fix_login_issue.py")

if __name__ == "__main__":
    main()

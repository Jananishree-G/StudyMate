#!/usr/bin/env python3
"""
Fix Login Issue - Create Test User and Verify Authentication
"""

import requests
import json
import sqlite3
import time
from datetime import datetime

API_BASE_URL = "http://localhost:8000"

def test_api_connection():
    """Test if API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/")
        return response.status_code == 200
    except:
        return False

def check_existing_users():
    """Check what users exist in database"""
    try:
        conn = sqlite3.connect("studymate.db")
        cursor = conn.cursor()
        cursor.execute("SELECT username, email FROM users ORDER BY created_at DESC LIMIT 10")
        users = cursor.fetchall()
        conn.close()
        return users
    except Exception as e:
        print(f"Database error: {e}")
        return []

def create_test_user():
    """Create a test user for login"""
    timestamp = str(int(time.time()))
    test_user = {
        "username": f"demo_{timestamp}",
        "email": f"demo_{timestamp}@studymate.com",
        "password": "demo123456",
        "full_name": "Demo User"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/auth/register", json=test_user)
        if response.status_code == 200:
            return test_user, response.json()
        else:
            error = response.json()
            return None, error
    except Exception as e:
        return None, str(e)

def test_login(username, password):
    """Test login with credentials"""
    try:
        response = requests.post(f"{API_BASE_URL}/auth/login", json={
            "username": username,
            "password": password
        })
        
        if response.status_code == 200:
            return True, response.json()
        else:
            error = response.json()
            return False, error
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 60)
    print("STUDYMATE LOGIN ISSUE TROUBLESHOOTING")
    print("=" * 60)
    
    # Step 1: Check API
    print("\n1. Checking API connection...")
    if not test_api_connection():
        print("ERROR: Backend API is not running!")
        print("Please start the backend with: python backend_api.py")
        return
    print("SUCCESS: Backend API is running")
    
    # Step 2: Check existing users
    print("\n2. Checking existing users...")
    users = check_existing_users()
    if users:
        print(f"Found {len(users)} existing users:")
        for username, email in users:
            print(f"  - {username} ({email})")
    else:
        print("No existing users found")
    
    # Step 3: Create test user
    print("\n3. Creating new test user...")
    user_data, result = create_test_user()
    
    if user_data:
        print("SUCCESS: Test user created!")
        print(f"Username: {user_data['username']}")
        print(f"Email: {user_data['email']}")
        print(f"Password: {user_data['password']}")
        
        # Step 4: Test login
        print("\n4. Testing login with new user...")
        success, login_result = test_login(user_data['username'], user_data['password'])
        
        if success:
            print("SUCCESS: Login working correctly!")
            print(f"User ID: {login_result['user']['id']}")
            print(f"Token received: Yes")
        else:
            print("ERROR: Login failed!")
            print(f"Error: {login_result}")
    else:
        print("ERROR: Could not create test user!")
        print(f"Error: {result}")
    
    # Step 5: Provide solution
    print("\n" + "=" * 60)
    print("SOLUTION FOR LOGIN ISSUE")
    print("=" * 60)
    
    if user_data:
        print("\nYou can now login with these credentials:")
        print(f"Username: {user_data['username']}")
        print(f"Password: {user_data['password']}")
        print("\nOR create a new account using the Register tab")
    
    print("\nCommon login issues and solutions:")
    print("1. WRONG PASSWORD: Make sure you're using the correct password")
    print("2. WRONG USERNAME: Check spelling and case sensitivity")
    print("3. USER NOT FOUND: Register a new account first")
    print("4. API CONNECTION: Ensure backend is running on port 8000")
    
    print("\nTo create a new account:")
    print("1. Go to http://localhost:8504")
    print("2. Click 'Register' tab")
    print("3. Fill in all required fields")
    print("4. Use a strong password (6+ characters)")
    print("5. Account will be created and you'll be logged in automatically")
    
    print("\nIf you forgot your password:")
    print("- Create a new account with a different username")
    print("- Or contact system administrator to reset password")

if __name__ == "__main__":
    main()

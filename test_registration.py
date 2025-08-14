#!/usr/bin/env python3
"""
Test Registration Functionality
Debug registration issues
"""

import requests
import json
from datetime import datetime

def test_registration():
    print("TESTING REGISTRATION FUNCTIONALITY")
    print("=" * 50)
    
    # Test backend connection
    print("\n1. Testing backend API...")
    try:
        response = requests.get('http://localhost:8000/')
        if response.status_code == 200:
            print("Backend API is running")
        else:
            print(f"Backend API error: {response.status_code}")
            return
    except Exception as e:
        print(f"Cannot connect to backend: {e}")
        return
    
    # Test registration
    print("\n2. Testing user registration...")
    timestamp = str(int(datetime.now().timestamp()))
    test_user = {
        'username': f'regtest_{timestamp}',
        'email': f'regtest_{timestamp}@studymate.com',
        'password': 'testpass123',
        'full_name': 'Registration Test User'
    }
    
    print(f"Attempting to register: {test_user['username']}")
    print(f"Email: {test_user['email']}")
    
    try:
        response = requests.post('http://localhost:8000/auth/register', 
                               json=test_user,
                               headers={'Content-Type': 'application/json'},
                               timeout=10)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Registration successful!")
            print(f"User ID: {result['user']['id']}")
            print(f"Username: {result['user']['username']}")
            print(f"Email: {result['user']['email']}")
            print(f"Token received: Yes ({len(result['access_token'])} chars)")
            
            # Test login with registered user
            print("\n3. Testing login with registered user...")
            login_response = requests.post('http://localhost:8000/auth/login',
                                         json={'username': test_user['username'], 
                                               'password': test_user['password']},
                                         timeout=10)
            
            if login_response.status_code == 200:
                print("Login successful!")
                return True
            else:
                print("Login failed!")
                print(login_response.json())
                
        else:
            print("Registration failed!")
            try:
                error = response.json()
                print(f"Error details: {error}")
            except:
                print(f"Raw response: {response.text}")
                
    except Exception as e:
        print(f"Registration error: {e}")
        import traceback
        traceback.print_exc()
    
    return False

def test_flask_registration():
    print("\n4. Testing Flask app registration...")
    
    # Test Flask registration endpoint
    test_data = {
        'username': f'flasktest_{int(datetime.now().timestamp())}',
        'email': f'flasktest_{int(datetime.now().timestamp())}@studymate.com',
        'password': 'testpass123',
        'full_name': 'Flask Test User'
    }
    
    try:
        # Test Flask registration form submission
        response = requests.post('http://localhost:8506/register',
                               data=test_data,
                               timeout=10)
        
        print(f"Flask registration response: {response.status_code}")
        
        if response.status_code == 200:
            print("Flask registration working!")
        else:
            print("Flask registration issue")
            print(response.text[:500])
            
    except Exception as e:
        print(f"Flask registration error: {e}")

if __name__ == "__main__":
    success = test_registration()
    test_flask_registration()
    
    if success:
        print("\nREGISTRATION SYSTEM IS WORKING!")
    else:
        print("\nREGISTRATION SYSTEM NEEDS FIXING!")

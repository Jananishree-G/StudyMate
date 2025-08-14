#!/usr/bin/env python3
"""
Test Registration Form
Simple form to test registration functionality
"""

from flask import Flask, render_template_string, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

API_BASE_URL = "http://localhost:8000"

TEST_FORM = """
<!DOCTYPE html>
<html>
<head>
    <title>Registration Test</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        button { width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .result { margin-top: 20px; padding: 15px; border-radius: 5px; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
        .info { background: #d1ecf1; color: #0c5460; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Registration Test Form</h1>
        
        <form id="regForm">
            <div class="form-group">
                <label>Username:</label>
                <input type="text" id="username" name="username" required>
            </div>
            
            <div class="form-group">
                <label>Email:</label>
                <input type="email" id="email" name="email" required>
            </div>
            
            <div class="form-group">
                <label>Full Name:</label>
                <input type="text" id="full_name" name="full_name">
            </div>
            
            <div class="form-group">
                <label>Password:</label>
                <input type="password" id="password" name="password" required minlength="6">
            </div>
            
            <button type="submit">Test Registration</button>
        </form>
        
        <div id="result"></div>
        
        <div class="info" style="margin-top: 20px;">
            <h3>Auto-fill Test Data</h3>
            <button onclick="fillTestData()">Fill Test Data</button>
        </div>
    </div>
    
    <script>
        function fillTestData() {
            const timestamp = Date.now();
            document.getElementById('username').value = `testuser_${timestamp}`;
            document.getElementById('email').value = `test_${timestamp}@studymate.com`;
            document.getElementById('full_name').value = 'Test User';
            document.getElementById('password').value = 'testpass123';
        }
        
        document.getElementById('regForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const data = Object.fromEntries(formData);
            
            document.getElementById('result').innerHTML = '<div class="info">Testing registration...</div>';
            
            try {
                const response = await fetch('/test_register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    document.getElementById('result').innerHTML = 
                        `<div class="success">
                            <h3>Registration Successful!</h3>
                            <p><strong>Username:</strong> ${result.user.username}</p>
                            <p><strong>Email:</strong> ${result.user.email}</p>
                            <p><strong>User ID:</strong> ${result.user.id}</p>
                            <p><strong>Token:</strong> ${result.token.substring(0, 20)}...</p>
                        </div>`;
                } else {
                    document.getElementById('result').innerHTML = 
                        `<div class="error">
                            <h3>Registration Failed!</h3>
                            <p>${result.error}</p>
                        </div>`;
                }
            } catch (error) {
                document.getElementById('result').innerHTML = 
                    `<div class="error">
                        <h3>Connection Error!</h3>
                        <p>${error.message}</p>
                    </div>`;
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(TEST_FORM)

@app.route('/test_register', methods=['POST'])
def test_register():
    """Test registration endpoint"""
    data = request.get_json()
    
    print(f"Registration test data: {data}")
    
    try:
        # Test backend connection
        backend_response = requests.get(f"{API_BASE_URL}/", timeout=5)
        if backend_response.status_code != 200:
            return jsonify({
                'success': False,
                'error': 'Backend API is not running'
            })
        
        # Attempt registration
        response = requests.post(f"{API_BASE_URL}/auth/register",
                               json=data,
                               headers={'Content-Type': 'application/json'},
                               timeout=10)
        
        print(f"Backend response status: {response.status_code}")
        print(f"Backend response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            return jsonify({
                'success': True,
                'user': result['user'],
                'token': result['access_token']
            })
        else:
            error_data = response.json() if response.headers.get('content-type') == 'application/json' else {'detail': response.text}
            return jsonify({
                'success': False,
                'error': error_data.get('detail', 'Registration failed')
            })
            
    except Exception as e:
        print(f"Registration test error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    print("=" * 60)
    print("REGISTRATION TEST FORM")
    print("=" * 60)
    print("URL: http://localhost:8508")
    print("This form will test registration functionality")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=8508, debug=True)

#!/usr/bin/env python3
"""
Flask-based StudyMate Login Page
Simple HTML login interface that definitely works
"""

from flask import Flask, render_template_string, request, redirect, url_for, flash, session
import requests
import json

app = Flask(__name__)
app.secret_key = 'studymate-secret-key'

API_BASE_URL = "http://localhost:8000"

# HTML Templates
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>StudyMate - Login</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 400px; margin: 50px auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .header { text-align: center; color: #333; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; color: #555; }
        input[type="text"], input[type="email"], input[type="password"] { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 16px; }
        .btn { width: 100%; padding: 12px; background: #667eea; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; margin-top: 10px; }
        .btn:hover { background: #5a6fd8; }
        .btn-secondary { background: #6c757d; }
        .btn-secondary:hover { background: #5a6268; }
        .alert { padding: 10px; margin-bottom: 20px; border-radius: 5px; }
        .alert-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .alert-error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .alert-info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
        .tabs { display: flex; margin-bottom: 20px; }
        .tab { flex: 1; padding: 10px; text-align: center; background: #f8f9fa; border: 1px solid #ddd; cursor: pointer; }
        .tab.active { background: #667eea; color: white; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .test-creds { background: #e9ecef; padding: 15px; border-radius: 5px; margin-top: 20px; }
        .test-creds h4 { margin-top: 0; color: #495057; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 StudyMate</h1>
            <p>AI Academic Assistant</p>
        </div>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'success' if category == 'success' else 'error' }}">
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <div class="tabs">
            <div class="tab active" onclick="showTab('login')">🔑 Login</div>
            <div class="tab" onclick="showTab('register')">📝 Register</div>
        </div>
        
        <!-- Login Tab -->
        <div id="login" class="tab-content active">
            <form method="POST" action="/login">
                <div class="form-group">
                    <label for="username">Username:</label>
                    <input type="text" id="username" name="username" required>
                </div>
                <div class="form-group">
                    <label for="password">Password:</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <button type="submit" class="btn">🔑 Login</button>
            </form>
        </div>
        
        <!-- Register Tab -->
        <div id="register" class="tab-content">
            <form method="POST" action="/register">
                <div class="form-group">
                    <label for="reg_username">Username:</label>
                    <input type="text" id="reg_username" name="username" required>
                </div>
                <div class="form-group">
                    <label for="reg_email">Email:</label>
                    <input type="email" id="reg_email" name="email" required>
                </div>
                <div class="form-group">
                    <label for="reg_full_name">Full Name (optional):</label>
                    <input type="text" id="reg_full_name" name="full_name">
                </div>
                <div class="form-group">
                    <label for="reg_password">Password:</label>
                    <input type="password" id="reg_password" name="password" required minlength="6">
                </div>
                <button type="submit" class="btn">📝 Register</button>
            </form>
        </div>
        
        <div class="test-creds">
            <h4>🧪 Test Credentials</h4>
            <strong>Username:</strong> demo_1755150234<br>
            <strong>Password:</strong> demo123456
        </div>
    </div>
    
    <script>
        function showTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }
    </script>
</body>
</html>
"""

REDIRECT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>StudyMate - Redirecting...</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center; }
        .container { max-width: 600px; margin: 100px auto; }
        .spinner { border: 4px solid rgba(255,255,255,0.3); border-radius: 50%; border-top: 4px solid white; width: 50px; height: 50px; animation: spin 1s linear infinite; margin: 20px auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .btn { padding: 12px 24px; background: rgba(255,255,255,0.2); color: white; border: 2px solid white; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; margin: 10px; }
        .btn:hover { background: rgba(255,255,255,0.3); }
    </style>
    <script>
        // Check if main app is available before redirecting
        function checkMainApp() {
            // Prepare authentication parameters
            const userDataEncoded = encodeURIComponent('{{ user | tojson }}');
            const redirectUrl = `http://localhost:8511/?auth=success&user=${userDataEncoded}&token={{ session.get('token', '') }}`;

            fetch('http://localhost:8511/')
                .then(response => {
                    if (response.ok) {
                        // Main app is available, redirect with auth params
                        window.location.href = redirectUrl;
                    } else {
                        // Main app not available, show manual link
                        document.getElementById('status').innerHTML =
                            '<p style="color: #ffeb3b;">⚠️ Main app not responding. Please click the link below.</p>';
                        document.getElementById('manual-link').href = redirectUrl;
                    }
                })
                .catch(error => {
                    // Connection failed, show manual link
                    document.getElementById('status').innerHTML =
                        '<p style="color: #ffeb3b;">⚠️ Main app not available. Please start it first.</p>';
                    document.getElementById('manual-link').href = redirectUrl;
                });
        }

        // Auto-redirect after 3 seconds
        setTimeout(checkMainApp, 3000);
    </script>
</head>
<body>
    <div class="container">
        <h1>🎉 Login Successful!</h1>
        <h2>Welcome {{ user.username }}!</h2>

        <div class="spinner"></div>

        <p style="font-size: 1.2rem; margin: 30px 0;">
            Redirecting you to StudyMate application...
        </p>

        <div id="status"></div>

        <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; margin: 30px 0;">
            <h3>✅ Authentication Successful</h3>
            <p><strong>Username:</strong> {{ user.username }}</p>
            <p><strong>Email:</strong> {{ user.email }}</p>
            <p><strong>Status:</strong> Logged in and verified</p>
        </div>

        <p>If you're not redirected automatically:</p>
        <a href="http://localhost:8511" id="manual-link" class="btn">🚀 Go to StudyMate App</a>
        <a href="/logout" class="btn">🚪 Logout</a>

        <div style="margin-top: 40px; font-size: 0.9rem; opacity: 0.8;">
            <p>🔐 Your session is secure and active</p>
            <p>📚 Ready to upload PDFs and chat with AI</p>
        </div>
    </div>
</body>
</html>
"""

def test_backend():
    """Test if backend API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False

def test_main_app():
    """Test if main StudyMate app is running"""
    try:
        response = requests.get("http://localhost:8510/", timeout=5)
        return response.status_code == 200
    except:
        return False

@app.route('/')
def index():
    """Main page"""
    if 'user' in session:
        return render_template_string(REDIRECT_TEMPLATE, user=session['user'])
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/login', methods=['POST'])
def login():
    """Handle login"""
    print(f"Login attempt - Form data: {dict(request.form)}")

    if not test_backend():
        flash('Backend API is not running! Please start: python backend_api.py', 'error')
        return redirect(url_for('index'))

    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()

    print(f"Login data - Username: {username}, Password length: {len(password)}")

    if not username or not password:
        flash('Username and password are required!', 'error')
        return redirect(url_for('index'))

    try:
        login_data = {"username": username, "password": password}
        print(f"Sending login request for user: {username}")

        response = requests.post(f"{API_BASE_URL}/auth/login",
                               json=login_data,
                               headers={'Content-Type': 'application/json'},
                               timeout=10)

        print(f"Login response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            session['user'] = data['user']
            session['token'] = data['access_token']
            flash(f'Login successful! Welcome back {username}!', 'success')
            print(f"Login successful for user: {username}")
            return redirect(url_for('index'))
        else:
            try:
                error = response.json()
                error_msg = error.get('detail', 'Unknown error')
                flash(f"Login failed: {error_msg}", 'error')
                print(f"Login failed: {error}")
            except:
                flash(f"Login failed: Server error (Status: {response.status_code})", 'error')
                print(f"Login failed with status: {response.status_code}")
    except Exception as e:
        flash(f"Connection error: {str(e)}", 'error')
        print(f"Login exception: {e}")

    return redirect(url_for('index'))

@app.route('/register', methods=['POST'])
def register():
    """Handle registration"""
    print(f"Registration attempt - Form data: {dict(request.form)}")

    if not test_backend():
        flash('Backend API is not running! Please start: python backend_api.py', 'error')
        return redirect(url_for('index'))

    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()
    full_name = request.form.get('full_name', '').strip()

    print(f"Registration data - Username: {username}, Email: {email}, Password length: {len(password)}")

    # Validation
    if not username:
        flash('Username is required!', 'error')
        return redirect(url_for('index'))

    if not email:
        flash('Email is required!', 'error')
        return redirect(url_for('index'))

    if not password:
        flash('Password is required!', 'error')
        return redirect(url_for('index'))

    if len(password) < 6:
        flash('Password must be at least 6 characters long!', 'error')
        return redirect(url_for('index'))

    try:
        registration_data = {
            "username": username,
            "email": email,
            "password": password,
            "full_name": full_name
        }

        print(f"Sending registration request: {registration_data}")

        response = requests.post(f"{API_BASE_URL}/auth/register",
                               json=registration_data,
                               headers={'Content-Type': 'application/json'},
                               timeout=10)

        print(f"Registration response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            session['user'] = data['user']
            session['token'] = data['access_token']
            flash(f'Registration successful! Welcome {username}!', 'success')
            print(f"Registration successful for user: {username}")
            return redirect(url_for('index'))
        else:
            try:
                error = response.json()
                error_msg = error.get('detail', 'Unknown error')
                flash(f"Registration failed: {error_msg}", 'error')
                print(f"Registration failed: {error}")
            except:
                flash(f"Registration failed: Server error (Status: {response.status_code})", 'error')
                print(f"Registration failed with status: {response.status_code}")
    except Exception as e:
        flash(f"Connection error: {str(e)}", 'error')
        print(f"Registration exception: {e}")

    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    """Handle logout"""
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 STARTING STUDYMATE FLASK LOGIN APP")
    print("=" * 60)
    print("📚 StudyMate Login Page")
    print("🌐 URL: http://localhost:8506")
    print("✅ This login page will definitely work!")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=8506, debug=True)

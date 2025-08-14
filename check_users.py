#!/usr/bin/env python3
"""
Check Users in Database
"""

import sqlite3

def check_users():
    print("CHECKING EXISTING USERS IN DATABASE")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('studymate.db')
        cursor = conn.cursor()
        
        # Get all users
        cursor.execute('SELECT username, email, created_at FROM users ORDER BY created_at DESC')
        users = cursor.fetchall()
        
        print(f"Total users in database: {len(users)}")
        print()
        
        if users:
            print("Existing users:")
            for i, (username, email, created_at) in enumerate(users, 1):
                print(f"   {i}. {username} ({email}) - {created_at[:19]}")
                
            # Check for the specific user trying to register
            cursor.execute('SELECT username, email FROM users WHERE username = ? OR email = ?', 
                          ('Jananishree_G', 'jananishreeg1@gmail.com'))
            existing = cursor.fetchone()
            
            if existing:
                print()
                print("CONFLICT FOUND:")
                print(f"   Username or email already exists: {existing[0]} ({existing[1]})")
                print("   This is why registration is failing!")
            else:
                print()
                print("No conflict found - registration should work")
        else:
            print("No users in database")
        
        conn.close()
        
    except Exception as e:
        print(f"Database error: {e}")
    
    print()
    print("SOLUTIONS:")
    print("1. Try a different username (e.g., Jananishree_G_2025)")
    print("2. Try a different email address")
    print("3. Use existing account if you already registered")

if __name__ == "__main__":
    check_users()

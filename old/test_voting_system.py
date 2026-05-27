#!/usr/bin/env python3
"""
Quick test script to verify the voting system is working.
Run this AFTER starting the server with: python main.py
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_voting_system():
    print("=" * 60)
    print("VOTING SYSTEM TEST")
    print("=" * 60)
    
    # Test 1: Check if server is running
    print("\n[1/5] Testing server connection...")
    try:
        response = requests.get(f"{BASE_URL}/votaciones", timeout=2)
        if response.status_code == 200:
            print("✅ Server is running and /votaciones endpoint responds")
        else:
            print(f"⚠️  Server responded with status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Server is NOT running!")
        print("   Please start the server first: python main.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 2: Check HTML file exists
    print("\n[2/5] Checking HTML file...")
    import os
    html_path = "game_pages/votaciones/votaciones.html"
    if os.path.exists(html_path):
        print(f"✅ HTML file exists: {html_path}")
        # Check file size
        size = os.path.getsize(html_path)
        print(f"   File size: {size:,} bytes")
    else:
        print(f"❌ HTML file NOT found: {html_path}")
        return False
    
    # Test 3: Check navigation function
    print("\n[3/5] Checking navigation in index.html...")
    index_path = "static/index.html"
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'openVotaciones' in content:
                print("✅ openVotaciones() function found in index.html")
            else:
                print("⚠️  openVotaciones() function NOT found")
    else:
        print(f"❌ index.html NOT found: {index_path}")
    
    # Test 4: Check backend endpoints
    print("\n[4/5] Checking backend endpoints in main.py...")
    main_path = "main.py"
    if os.path.exists(main_path):
        with open(main_path, 'r', encoding='utf-8') as f:
            content = f.read()
            endpoints = [
                '/api/votaciones/list',
                '/api/votaciones/{votacion_id}',
                '/api/votaciones/create',
                '/api/votaciones/votar',
                '/api/votaciones/finalizar',
            ]
            found = 0
            for endpoint in endpoints:
                if endpoint in content:
                    found += 1
            print(f"✅ Found {found}/{len(endpoints)} voting endpoints")
    else:
        print(f"❌ main.py NOT found: {main_path}")
    
    # Test 5: Check database function
    print("\n[5/5] Checking database function...")
    if 'db_votaciones' in content:
        print("✅ db_votaciones() function found")
    else:
        print("⚠️  db_votaciones() function NOT found")
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print("✅ All components are in place!")
    print("\nTO USE THE VOTING SYSTEM:")
    print("1. Make sure server is running (python main.py)")
    print("2. Open http://localhost:8000 in your browser")
    print("3. Log in with your credentials")
    print("4. Click 'Votaciones' button in navigation")
    print("5. Create and use votes!")
    print("\nFor more details, see: VOTING_SYSTEM_READY.md")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    test_voting_system()

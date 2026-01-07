#!/usr/bin/env python3
"""Debug script for iQua API - shows full HTTP request/response"""

import sys
import json
import logging

# Setup detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Install required packages
try:
    import requests
except ImportError:
    print("Installing requests...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "requests"])
    import requests

# Enable HTTP debug logging
import http.client as http_client
http_client.HTTPConnection.debuglevel = 1

# Test credentials
USERNAME = "corapoid@gmail.com"
PASSWORD = "X%g5lbt+00"
SERIAL_NUMBER = input("Enter Device Serial Number (DSN#): ").strip()

print("\n" + "="*80)
print("🔍 DETAILED API DEBUG TEST")
print("="*80)
print(f"Username: {USERNAME}")
print(f"Password: {PASSWORD}")
print(f"Serial:   {SERIAL_NUMBER}")
print("="*80)
print()

# Test 1: Basic auth
print("📡 TEST 1: Authentication with default settings")
print("-"*80)

url = "https://apioem.ecowater.com/v1/auth/signin"
headers = {
    "User-Agent": "okhttp/4.9.1",
    "Content-Type": "application/json",
    "Accept": "application/json"
}
payload = {
    "username": USERNAME,
    "password": PASSWORD
}

print(f"POST {url}")
print(f"Headers: {json.dumps(headers, indent=2)}")
print(f"Payload: {json.dumps(payload, indent=2)}")
print()

try:
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    
    print(f"✅ Response received")
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers:")
    for key, value in response.headers.items():
        print(f"  {key}: {value}")
    print()
    print(f"Response Body:")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
    print()
    
    if response.status_code == 200:
        print("✅ SUCCESS! Authentication worked!")
        data = response.json()
        if data.get("code") == "OK":
            token = data.get("data", {}).get("token")
            print(f"✅ Token received: {token[:20]}...")
            
            # Test 2: Fetch device data
            print("\n" + "="*80)
            print("📡 TEST 2: Fetching device data")
            print("-"*80)
            
            device_url = f"https://apioem.ecowater.com/v1/system/{SERIAL_NUMBER}/dashboard"
            auth_headers = headers.copy()
            auth_headers["Authorization"] = f"{data['data']['tokenType']} {token}"
            
            print(f"GET {device_url}")
            print(f"Headers: {json.dumps(auth_headers, indent=2)}")
            print()
            
            device_response = requests.get(device_url, headers=auth_headers, timeout=10)
            print(f"Status Code: {device_response.status_code}")
            print(f"Response Body:")
            try:
                print(json.dumps(device_response.json(), indent=2))
            except:
                print(device_response.text)
            
            if device_response.status_code == 200:
                print("\n✅ ✅ ✅ FULL SUCCESS! Everything works!")
            else:
                print(f"\n⚠️  Device data fetch failed with {device_response.status_code}")
        else:
            print(f"⚠️  Response code: {data.get('code')} - {data.get('message')}")
    else:
        print(f"❌ Authentication failed with status {response.status_code}")
        
except requests.exceptions.RequestException as e:
    print(f"❌ Request failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("🔍 DEBUG TEST COMPLETE")
print("="*80)

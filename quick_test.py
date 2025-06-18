#!/usr/bin/env python3
import requests
import json

print("🎯 Testing Advice Mode Endpoint...")

# Test advice mode
url = 'http://localhost:8000/analyze/'
files = {'file': ('test.txt', b'fake image data', 'image/jpeg')}
data = {'players': 'advice'}

try:
    response = requests.post(url, files=files, data=data, timeout=10)
    print('Status:', response.status_code)
    print('Response:', response.text[:500])
    
    if response.status_code == 200:
        result = response.json()
        if 'advice' in result:
            print("✅ Advice mode endpoint working!")
        else:
            print("❌ No advice in response")
    else:
        print(f"❌ Error status: {response.status_code}")
        
except Exception as e:
    print('Error:', e)

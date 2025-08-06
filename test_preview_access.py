#!/usr/bin/env python3
"""Test if preview server is accessible"""

import requests
import sys

ports_to_test = [5000, 5001, 5002, 5003, 5004]

print("🔍 Testing preview server accessibility...\n")

for port in ports_to_test:
    url = f"http://localhost:{port}/preview"
    try:
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            print(f"✅ Port {port}: SUCCESS - Preview server is running!")
            print(f"   URL: http://localhost:{port}/preview")
            print(f"   Response size: {len(response.content)} bytes")
            print(f"\n🌐 Open this URL in your browser: http://localhost:{port}/preview\n")
            
            # Test API endpoint
            api_url = f"http://localhost:{port}/api/preview/status"
            try:
                api_response = requests.get(api_url, timeout=2)
                if api_response.status_code == 200:
                    print(f"✅ API endpoint is working: {api_response.json()}")
            except:
                pass
            
            sys.exit(0)
        else:
            print(f"❌ Port {port}: Server responded with status {response.status_code}")
    except requests.exceptions.ConnectionRefusedError:
        print(f"❌ Port {port}: Connection refused")
    except requests.exceptions.Timeout:
        print(f"❌ Port {port}: Timeout")
    except Exception as e:
        print(f"❌ Port {port}: Error - {str(e)}")

print("\n❌ No preview server found on any tested port!")
print("\nTry running: ./start_preview_server.sh")
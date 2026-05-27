import requests

url = "https://striking-symphony-mummify.ngrok-free.dev/apuestas?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkdmQiLCJleHAiOjE3Nzg1NDQ3MzV9.9owpOmSmSk3GC1PLE6pZ9DpOED62MgSK0RZgJCnpHek"

try:
    response = requests.get(url, timeout=10)
    print(f"Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"Error: {response.text[:500]}")
    else:
        # Check if there's JavaScript error in the HTML
        html = response.text
        if "error" in html.lower() or "undefined" in html.lower():
            print("Found potential error in HTML")
            # Find error context
            lines = html.split('\n')
            for i, line in enumerate(lines):
                if 'error' in line.lower() or 'undefined' in line.lower():
                    print(f"Line {i}: {line[:200]}")
        else:
            print("Page loaded successfully, no obvious errors")
            
except Exception as e:
    print(f"Request failed: {e}")

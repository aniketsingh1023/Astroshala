import requests
import json

# Test API endpoints
base_url = "http://localhost:5000"

def test_endpoint(method, endpoint, data=None):
    """Test an API endpoint with the given method and data"""
    url = f"{base_url}{endpoint}"
    
    # First test OPTIONS request
    options_response = requests.options(
        url, 
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": method,
            "Access-Control-Request-Headers": "Content-Type,Authorization"
        }
    )
    
    print(f"OPTIONS {endpoint}: {options_response.status_code}")
    if options_response.status_code != 200:
        print(f"  Headers: {dict(options_response.headers)}")
        print(f"  Response: {options_response.text}")
    
    # Then test the actual method
    if method == "GET":
        response = requests.get(url)
    elif method == "POST":
        response = requests.post(url, json=data)
    else:
        return
    
    print(f"{method} {endpoint}: {response.status_code}")
    if response.status_code != 200:
        print(f"  Response: {response.text}")
    else:
        print(f"  Success!")

# Test endpoints
print("Testing API endpoints...")
test_endpoint("GET", "/api/health")

# Test chat query endpoint
test_endpoint("POST", "/api/chat/query", {
    "message": "What is Vedic astrology?",
    "conversation_history": []
})

print("\nDone!")
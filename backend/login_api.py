import requests
import json

# Configuration
API_BASE_URL = "http://localhost:5000"

def test_chat_api():
    """Test the chat API endpoints"""
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{API_BASE_URL}/")
        print(f"Server check: {'✅ OK' if response.status_code == 200 else '❌ Failed'}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Server check error: {e}")
    
    print("\n" + "-"*50 + "\n")
    
    # Test 2: Direct test endpoint (should work without auth)
    try:
        response = requests.post(
            f"{API_BASE_URL}/direct-test", 
            json={"test": "data"}
        )
        print(f"Direct test: {'✅ OK' if response.status_code == 200 else '❌ Failed'}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Direct test error: {e}")
    
    print("\n" + "-"*50 + "\n")
    
    # Test 3: Public chat query endpoint
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/chat/public/query", 
            json={"message": "What are the nine planets in Vedic astrology?"}
        )
        print(f"Public chat query: {'✅ OK' if response.status_code == 200 else '❌ Failed'}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Public chat query error: {e}")

if __name__ == "__main__":
    test_chat_api()
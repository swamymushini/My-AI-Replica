#!/usr/bin/env python3
"""
Test script for the Enhanced AI Replica API
This script demonstrates how to use the API with both GET and POST requests
"""

import requests
import json
import time

def test_get_request():
    """Test GET request to the API"""
    print("=== Testing GET Request ===")
    
    # Test with a simple query
    query = "What is your experience with Java?"
    url = f"http://localhost:8000/?query={query}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()
            print("✅ GET Request Successful!")
            print(f"Query: {result['query']}")
            print(f"Response: {result['response']}")
            print(f"Relevant Context: {json.dumps(result['relevant_context'], indent=2)}")
        else:
            print(f"❌ GET Request Failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error in GET request: {e}")

def test_post_request():
    """Test POST request to the API"""
    print("\n=== Testing POST Request ===")
    
    url = "http://localhost:8000/"
    data = {
        "query": "Tell me about your AWS experience"
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            print("✅ POST Request Successful!")
            print(f"Query: {result['query']}")
            print(f"Response: {result['response']}")
            print(f"Relevant Context: {json.dumps(result['relevant_context'], indent=2)}")
        else:
            print(f"❌ POST Request Failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error in POST request: {e}")

def test_api_info():
    """Test getting API information"""
    print("\n=== Testing API Info ===")
    
    url = "http://localhost:8000/"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()
            print("✅ API Info Retrieved Successfully!")
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ API Info Request Failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error getting API info: {e}")

def test_various_queries():
    """Test various types of queries"""
    print("\n=== Testing Various Queries ===")
    
    queries = [
        "What is your name?",
        "How many years of experience do you have?",
        "What technologies do you work with?",
        "Tell me about your projects",
        "What is your current location?",
        "What is your notice period?"
    ]
    
    for query in queries:
        print(f"\n--- Testing: {query} ---")
        url = f"http://localhost:8000/?query={query}"
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                result = response.json()
                print(f"Response: {result['response'][:200]}...")
            else:
                print(f"Failed: {response.status_code}")
        except Exception as e:
            print(f"Error: {e}")
        
        # Small delay to avoid rate limiting
        time.sleep(1)

if __name__ == "__main__":
    print("🚀 Enhanced AI Replica API Test Suite")
    print("Make sure the API is running on http://localhost:8000")
    print("=" * 50)
    
    # Test API info first
    test_api_info()
    
    # Test basic functionality
    test_get_request()
    test_post_request()
    
    # Test various queries
    test_various_queries()
    
    print("\n" + "=" * 50)
    print("✅ Test suite completed!")
    print("\nTo run the API server:")
    print("python api/enhanced_api.py")

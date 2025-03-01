#!/usr/bin/env python
"""
ServiceNow Connection Test Script

This script tests the connection to a ServiceNow instance using the credentials
provided in the .env file. It supports all authentication methods:
- Basic authentication (username/password)
- OAuth authentication (client ID/client secret)
- API key authentication

Usage:
    python scripts/test_connection.py
"""

import os
import sys
import requests
import base64
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

def get_oauth_token(instance_url, client_id, client_secret, username=None, password=None):
    """Get an OAuth token from ServiceNow."""
    token_url = os.getenv("SERVICENOW_TOKEN_URL", f"{instance_url}/oauth_token.do")
    
    # Create authorization header
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    
    # Try different OAuth grant types
    access_token = None
    
    # 1. Try client credentials grant
    try:
        print("Attempting client_credentials grant...")
        token_response = requests.post(
            token_url,
            headers={
                "Authorization": f"Basic {auth_header}",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data={
                "grant_type": "client_credentials"
            }
        )
        
        if token_response.status_code == 200:
            token_data = token_response.json()
            access_token = token_data.get("access_token")
            print("✅ Successfully obtained OAuth token using client_credentials grant!")
            return access_token
        else:
            print(f"❌ Failed with client_credentials grant: {token_response.status_code}")
            print(f"Response: {token_response.text}")
    except Exception as e:
        print(f"❌ Error with client_credentials grant: {e}")
    
    # 2. Try password grant if client credentials failed and we have username/password
    if not access_token and username and password:
        try:
            print("Attempting password grant...")
            token_response = requests.post(
                token_url,
                headers={
                    "Authorization": f"Basic {auth_header}",
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                data={
                    "grant_type": "password",
                    "username": username,
                    "password": password
                }
            )
            
            if token_response.status_code == 200:
                token_data = token_response.json()
                access_token = token_data.get("access_token")
                print("✅ Successfully obtained OAuth token using password grant!")
                return access_token
            else:
                print(f"❌ Failed with password grant: {token_response.status_code}")
                print(f"Response: {token_response.text}")
        except Exception as e:
            print(f"❌ Error with password grant: {e}")
    
    return None

def test_connection():
    # Load environment variables
    load_dotenv()
    
    # Print all environment variables related to ServiceNow
    print("Environment variables:")
    for key, value in os.environ.items():
        if "SERVICENOW" in key:
            masked_value = value
            if "PASSWORD" in key or "SECRET" in key:
                masked_value = "*" * len(value)
            print(f"  {key}={masked_value}")
    print()
    
    # Get ServiceNow credentials
    instance_url = os.getenv("SERVICENOW_INSTANCE_URL")
    auth_type = os.getenv("SERVICENOW_AUTH_TYPE", "basic")
    
    # Check if instance URL is set
    if not instance_url or instance_url == "https://your-instance.service-now.com":
        print("Error: ServiceNow instance URL is not set or is using the default value.")
        print("Please update the SERVICENOW_INSTANCE_URL in your .env file.")
        sys.exit(1)
    
    print(f"Testing connection to ServiceNow instance: {instance_url}")
    print(f"Authentication type: {auth_type}")
    
    # Construct API endpoint URL
    api_url = f"{instance_url}/api/now/table/incident?sysparm_limit=1"
    headers = {"Accept": "application/json"}
    auth = None
    
    # Set up authentication based on auth type
    if auth_type == "basic":
        username = os.getenv("SERVICENOW_USERNAME")
        password = os.getenv("SERVICENOW_PASSWORD")
        
        if not username or not password or username == "your-username" or password == "your-password":
            print("Error: Username or password is not set or is using the default value.")
            print("Please update the SERVICENOW_USERNAME and SERVICENOW_PASSWORD in your .env file.")
            sys.exit(1)
            
        auth = (username, password)
        print("Using basic authentication (username/password)")
        print(f"Username: {username}")
        print(f"Password: {'*' * len(password)}")
        
    elif auth_type == "oauth":
        client_id = os.getenv("SERVICENOW_CLIENT_ID")
        client_secret = os.getenv("SERVICENOW_CLIENT_SECRET")
        username = os.getenv("SERVICENOW_USERNAME")
        password = os.getenv("SERVICENOW_PASSWORD")
        
        if not client_id or not client_secret or client_id == "your-client-id" or client_secret == "your-client-secret":
            print("Error: Client ID or Client Secret is not set or is using the default value.")
            print("Please update the SERVICENOW_CLIENT_ID and SERVICENOW_CLIENT_SECRET in your .env file.")
            print("You can run scripts/setup_oauth.py to set up OAuth authentication.")
            sys.exit(1)
            
        print("Using OAuth authentication (client ID/client secret)")
        access_token = get_oauth_token(instance_url, client_id, client_secret, username, password)
        
        if not access_token:
            print("Failed to obtain OAuth token. Please check your credentials.")
            sys.exit(1)
            
        headers["Authorization"] = f"Bearer {access_token}"
        
    elif auth_type == "api_key":
        api_key = os.getenv("SERVICENOW_API_KEY")
        api_key_header = os.getenv("SERVICENOW_API_KEY_HEADER", "X-ServiceNow-API-Key")
        
        if not api_key or api_key == "your-api-key":
            print("Error: API key is not set or is using the default value.")
            print("Please update the SERVICENOW_API_KEY in your .env file.")
            print("You can run scripts/setup_api_key.py to set up API key authentication.")
            sys.exit(1)
            
        print(f"Using API key authentication (header: {api_key_header})")
        headers[api_key_header] = api_key
        
    else:
        print(f"Error: Unsupported authentication type: {auth_type}")
        print("Supported types: basic, oauth, api_key")
        sys.exit(1)
    
    try:
        # Print request details
        print("\nRequest details:")
        print(f"URL: {api_url}")
        print(f"Headers: {headers}")
        if auth:
            print(f"Auth: ({auth[0]}, {'*' * len(auth[1])})")
        
        # Make a test request
        if auth:
            response = requests.get(api_url, auth=auth, headers=headers)
        else:
            response = requests.get(api_url, headers=headers)
        
        # Print response details
        print("\nResponse details:")
        print(f"Status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        # Check response
        if response.status_code == 200:
            print("\n✅ Connection successful!")
            data = response.json()
            print(f"Retrieved {len(data.get('result', []))} incident(s)")
            print("\nSample response:")
            print(f"{response.text[:500]}...")
            return True
        else:
            print(f"\n❌ Connection failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    test_connection() 
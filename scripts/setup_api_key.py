#!/usr/bin/env python
"""
ServiceNow API Key Setup Script

This script helps set up and test API key authentication with ServiceNow.
It will:
1. Test the API key with a simple API call
2. Update the .env file with the API key configuration

Usage:
    python scripts/setup_api_key.py
"""

import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

def setup_api_key():
    # Load environment variables
    load_dotenv()
    
    # Get ServiceNow instance URL
    instance_url = os.getenv("SERVICENOW_INSTANCE_URL")
    if not instance_url or instance_url == "https://your-instance.service-now.com":
        instance_url = input("Enter your ServiceNow instance URL (e.g., https://dev296866.service-now.com): ")
    
    print("\n=== ServiceNow API Key Setup ===")
    print("This script will help you set up API key authentication for your ServiceNow instance.")
    print("You'll need to create an API key in ServiceNow first.")
    print("\nTo create an API key in a Personal Developer Instance (PDI):")
    print("1. Log in to your ServiceNow instance")
    print("2. Navigate to User Profile > REST API Keys")
    print("3. Click 'New'")
    print("4. Fill in the required fields and save")
    print("5. Copy the API key (you'll only see it once)")
    
    # Get API key
    api_key = input("\nEnter your API key: ")
    api_key_header = input("Enter the API key header name (default: X-ServiceNow-API-Key): ") or "X-ServiceNow-API-Key"
    
    print(f"\nTesting API key connection to {instance_url}...")
    
    # Test the API key
    try:
        # Make a test request
        test_url = f"{instance_url}/api/now/table/incident?sysparm_limit=1"
        test_response = requests.get(
            test_url,
            headers={
                api_key_header: api_key,
                'Accept': 'application/json'
            }
        )
        
        if test_response.status_code == 200:
            print("✅ Successfully tested API key with API call!")
            data = test_response.json()
            print(f"Retrieved {len(data.get('result', []))} incident(s)")
            
            # Update .env file
            update_env = input("\nDo you want to update your .env file with this API key? (y/n): ")
            if update_env.lower() == 'y':
                env_path = Path(__file__).parent.parent / '.env'
                with open(env_path, 'r') as f:
                    env_content = f.read()
                
                # Update API key configuration
                env_content = env_content.replace('SERVICENOW_AUTH_TYPE=basic', 'SERVICENOW_AUTH_TYPE=api_key')
                env_content = env_content.replace('# SERVICENOW_API_KEY=your-api-key', f'SERVICENOW_API_KEY={api_key}')
                env_content = env_content.replace('# SERVICENOW_API_KEY_HEADER=X-ServiceNow-API-Key', f'SERVICENOW_API_KEY_HEADER={api_key_header}')
                
                with open(env_path, 'w') as f:
                    f.write(env_content)
                
                print("✅ Updated .env file with API key configuration!")
                print("\nYou can now use API key authentication with the ServiceNow MCP server.")
                print("To test it, run: python scripts/test_connection.py")
            
            return True
        else:
            print(f"❌ Failed to test API key with API call: {test_response.status_code}")
            print(f"Response: {test_response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    setup_api_key() 
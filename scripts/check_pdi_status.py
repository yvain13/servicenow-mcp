#!/usr/bin/env python
"""
ServiceNow PDI Status Checker

This script checks the status of a ServiceNow PDI instance.
It will:
1. Check if the instance is reachable
2. Check if the instance is active or hibernating
3. Provide guidance on waking up a hibernating instance

Usage:
    python scripts/check_pdi_status.py
"""

import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

def check_instance_status(instance_url):
    """Check the status of a ServiceNow instance."""
    print(f"\nChecking instance status: {instance_url}")
    
    # Check if the instance is reachable
    try:
        # Try accessing the login page
        login_response = requests.get(f"{instance_url}/login.do", 
                                     allow_redirects=True,
                                     timeout=10)
        
        # Try accessing the API
        api_response = requests.get(f"{instance_url}/api/now/table/sys_properties?sysparm_limit=1", 
                                   headers={"Accept": "application/json"},
                                   timeout=10)
        
        # Check if the instance is hibernating
        if "instance is hibernating" in login_response.text.lower() or "instance is hibernating" in api_response.text.lower():
            print("❌ Instance is HIBERNATING")
            print("\nYour PDI is currently hibernating. To wake it up:")
            print("1. Go to https://developer.servicenow.com/")
            print("2. Log in with your ServiceNow account")
            print("3. Go to 'My Instances'")
            print("4. Find your PDI and click 'Wake'")
            print("5. Wait a few minutes for the instance to wake up")
            return False
        
        # Check if the instance is accessible
        if login_response.status_code == 200 and "ServiceNow" in login_response.text:
            print("✅ Instance is ACTIVE and accessible")
            print("✅ Login page is available")
            
            # Extract the instance name from the login page
            if "instance_name" in login_response.text:
                start_index = login_response.text.find("instance_name")
                end_index = login_response.text.find(";", start_index)
                if start_index > 0 and end_index > start_index:
                    instance_info = login_response.text[start_index:end_index]
                    print(f"Instance info: {instance_info}")
            
            return True
        else:
            print(f"❌ Instance returned unexpected status code: {login_response.status_code}")
            print("❌ Login page may not be accessible")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to instance: {e}")
        return False

def main():
    """Main function to run the PDI status checker."""
    load_dotenv()
    
    print("=" * 60)
    print("ServiceNow PDI Status Checker".center(60))
    print("=" * 60)
    
    # Get instance URL
    instance_url = os.getenv("SERVICENOW_INSTANCE_URL")
    if not instance_url or instance_url == "https://your-instance.service-now.com":
        instance_url = input("Enter your ServiceNow instance URL: ")
    
    # Check instance status
    is_active = check_instance_status(instance_url)
    
    if is_active:
        print("\nYour PDI is active. To find your credentials:")
        print("1. Go to https://developer.servicenow.com/")
        print("2. Log in with your ServiceNow account")
        print("3. Go to 'My Instances'")
        print("4. Find your PDI and click on it")
        print("5. Look for the credentials information")
        
        print("\nDefault PDI credentials are usually:")
        print("Username: admin")
        print("Password: (check on the developer portal)")
    else:
        print("\nPlease check your instance status on the ServiceNow Developer Portal.")
        print("If your instance is hibernating, you'll need to wake it up before you can connect.")

if __name__ == "__main__":
    main() 
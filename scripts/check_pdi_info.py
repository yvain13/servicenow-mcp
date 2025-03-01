#!/usr/bin/env python
"""
ServiceNow PDI Information Checker

This script helps determine the correct credentials for a ServiceNow PDI instance.
It will:
1. Check if the instance is reachable
2. Try different common username combinations
3. Provide guidance on finding the correct credentials

Usage:
    python scripts/check_pdi_info.py
"""

import os
import sys
import requests
from pathlib import Path
from getpass import getpass
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

def check_instance_info(instance_url):
    """Check basic information about the ServiceNow instance."""
    print(f"\nChecking instance: {instance_url}")
    
    # Check if the instance is reachable
    try:
        response = requests.get(f"{instance_url}/api/now/table/sys_properties?sysparm_limit=1", 
                               headers={"Accept": "application/json"})
        
        if response.status_code == 200:
            print("✅ Instance is reachable")
            print("❌ But authentication is required")
        elif response.status_code == 401:
            print("✅ Instance is reachable")
            print("❌ Authentication required")
        else:
            print(f"❌ Instance returned unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to instance: {e}")
        return False
    
    return True

def test_credentials(instance_url, username, password):
    """Test a set of credentials against the ServiceNow instance."""
    print(f"\nTesting credentials: {username} / {'*' * len(password)}")
    
    try:
        response = requests.get(
            f"{instance_url}/api/now/table/incident?sysparm_limit=1",
            auth=(username, password),
            headers={"Accept": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Authentication successful!")
            data = response.json()
            print(f"Retrieved {len(data.get('result', []))} incident(s)")
            return True
        else:
            print(f"❌ Authentication failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False

def main():
    """Main function to run the PDI checker."""
    load_dotenv()
    
    print("=" * 60)
    print("ServiceNow PDI Credential Checker".center(60))
    print("=" * 60)
    
    # Get instance URL
    instance_url = os.getenv("SERVICENOW_INSTANCE_URL")
    if not instance_url or instance_url == "https://your-instance.service-now.com":
        instance_url = input("Enter your ServiceNow instance URL: ")
    
    # Check if instance is reachable
    if not check_instance_info(instance_url):
        print("\nPlease check your instance URL and try again.")
        return
    
    print("\nFor a Personal Developer Instance (PDI), try these common usernames:")
    print("1. admin")
    print("2. Your ServiceNow account email")
    print("3. Your ServiceNow username (without @domain.com)")
    
    # Try with current credentials first
    current_username = os.getenv("SERVICENOW_USERNAME")
    current_password = os.getenv("SERVICENOW_PASSWORD")
    
    if current_username and current_password:
        print("\nTrying with current credentials from .env file...")
        if test_credentials(instance_url, current_username, current_password):
            print("\n✅ Your current credentials in .env are working!")
            return
    
    # Ask for new credentials
    print("\nLet's try with new credentials:")
    
    # Try admin
    print("\nTrying with 'admin' username...")
    admin_password = getpass("Enter password for 'admin' user (press Enter to skip): ")
    if admin_password and test_credentials(instance_url, "admin", admin_password):
        update = input("\nDo you want to update your .env file with these credentials? (y/n): ")
        if update.lower() == 'y':
            update_env_file(instance_url, "admin", admin_password)
        return
    
    # Try with email
    email = input("\nEnter your ServiceNow account email: ")
    if email:
        email_password = getpass(f"Enter password for '{email}': ")
        if test_credentials(instance_url, email, email_password):
            update = input("\nDo you want to update your .env file with these credentials? (y/n): ")
            if update.lower() == 'y':
                update_env_file(instance_url, email, email_password)
            return
    
    # Try with username only (no domain)
    if '@' in email:
        username = email.split('@')[0]
        print(f"\nTrying with username part only: '{username}'...")
        username_password = getpass(f"Enter password for '{username}': ")
        if test_credentials(instance_url, username, username_password):
            update = input("\nDo you want to update your .env file with these credentials? (y/n): ")
            if update.lower() == 'y':
                update_env_file(instance_url, username, username_password)
            return
    
    print("\n❌ None of the common credential combinations worked.")
    print("\nTo find your PDI credentials:")
    print("1. Go to https://developer.servicenow.com/")
    print("2. Log in with your ServiceNow account")
    print("3. Go to 'My Instances'")
    print("4. Find your PDI and click on it")
    print("5. Look for the credentials information")
    
    # Ask for custom credentials
    custom = input("\nDo you want to try custom credentials? (y/n): ")
    if custom.lower() == 'y':
        custom_username = input("Enter username: ")
        custom_password = getpass("Enter password: ")
        if test_credentials(instance_url, custom_username, custom_password):
            update = input("\nDo you want to update your .env file with these credentials? (y/n): ")
            if update.lower() == 'y':
                update_env_file(instance_url, custom_username, custom_password)

def update_env_file(instance_url, username, password):
    """Update the .env file with working credentials."""
    env_path = Path(__file__).parent.parent / '.env'
    with open(env_path, 'r') as f:
        env_content = f.read()
    
    # Update credentials
    env_content = env_content.replace(f'SERVICENOW_INSTANCE_URL={os.getenv("SERVICENOW_INSTANCE_URL", "https://your-instance.service-now.com")}', f'SERVICENOW_INSTANCE_URL={instance_url}')
    env_content = env_content.replace(f'SERVICENOW_USERNAME={os.getenv("SERVICENOW_USERNAME", "your-username")}', f'SERVICENOW_USERNAME={username}')
    env_content = env_content.replace(f'SERVICENOW_PASSWORD={os.getenv("SERVICENOW_PASSWORD", "your-password")}', f'SERVICENOW_PASSWORD={password}')
    
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print("✅ Updated .env file with working credentials!")

if __name__ == "__main__":
    main() 
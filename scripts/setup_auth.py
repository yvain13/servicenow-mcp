#!/usr/bin/env python
"""
ServiceNow Authentication Setup Menu

This script provides a menu to help users set up different authentication methods
for the ServiceNow MCP server.

Usage:
    python scripts/setup_auth.py
"""

import os
import sys
import subprocess
from pathlib import Path

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the header for the menu."""
    print("=" * 60)
    print("ServiceNow MCP Server - Authentication Setup".center(60))
    print("=" * 60)
    print("\nThis script will help you set up authentication for your ServiceNow instance.")
    print("Choose one of the following authentication methods:\n")

def print_menu():
    """Print the menu options."""
    print("1. Basic Authentication (username/password)")
    print("2. OAuth Authentication (client ID/client secret)")
    print("3. API Key Authentication")
    print("4. Test Current Configuration")
    print("5. Exit")
    print("\nEnter your choice (1-5): ", end="")

def setup_basic_auth():
    """Set up basic authentication."""
    clear_screen()
    print("=" * 60)
    print("Basic Authentication Setup".center(60))
    print("=" * 60)
    print("\nYou'll need your ServiceNow instance URL, username, and password.")
    
    instance_url = input("\nEnter your ServiceNow instance URL: ")
    username = input("Enter your ServiceNow username: ")
    password = input("Enter your ServiceNow password: ")
    
    # Update .env file
    env_path = Path(__file__).parent.parent / '.env'
    with open(env_path, 'r') as f:
        env_content = f.read()
    
    # Update basic authentication configuration
    env_content = env_content.replace('SERVICENOW_INSTANCE_URL=https://your-instance.service-now.com', f'SERVICENOW_INSTANCE_URL={instance_url}')
    env_content = env_content.replace('SERVICENOW_USERNAME=your-username', f'SERVICENOW_USERNAME={username}')
    env_content = env_content.replace('SERVICENOW_PASSWORD=your-password', f'SERVICENOW_PASSWORD={password}')
    
    # Ensure auth type is set to basic
    if 'SERVICENOW_AUTH_TYPE=oauth' in env_content:
        env_content = env_content.replace('SERVICENOW_AUTH_TYPE=oauth', 'SERVICENOW_AUTH_TYPE=basic')
    elif 'SERVICENOW_AUTH_TYPE=api_key' in env_content:
        env_content = env_content.replace('SERVICENOW_AUTH_TYPE=api_key', 'SERVICENOW_AUTH_TYPE=basic')
    
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print("\n✅ Updated .env file with basic authentication configuration!")
    input("\nPress Enter to continue...")

def main():
    """Main function to run the menu."""
    while True:
        clear_screen()
        print_header()
        print_menu()
        
        choice = input()
        
        if choice == '1':
            setup_basic_auth()
        elif choice == '2':
            # Run the OAuth setup script
            subprocess.run([sys.executable, str(Path(__file__).parent / 'setup_oauth.py')])
            input("\nPress Enter to continue...")
        elif choice == '3':
            # Run the API key setup script
            subprocess.run([sys.executable, str(Path(__file__).parent / 'setup_api_key.py')])
            input("\nPress Enter to continue...")
        elif choice == '4':
            # Run the test connection script
            clear_screen()
            print("Testing current configuration...\n")
            subprocess.run([sys.executable, str(Path(__file__).parent / 'test_connection.py')])
            input("\nPress Enter to continue...")
        elif choice == '5':
            clear_screen()
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main() 
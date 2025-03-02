#!/usr/bin/env python
"""
Wake ServiceNow Instance

This script attempts to wake up a hibernating ServiceNow instance by
making requests to it and following any redirects to the wake-up page.
"""

import os
import sys
import time
import logging
import requests
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def wake_instance(instance_url, max_attempts=5, wait_time=10):
    """
    Attempt to wake up a hibernating ServiceNow instance.
    
    Args:
        instance_url: The URL of the ServiceNow instance
        max_attempts: Maximum number of wake-up attempts
        wait_time: Time to wait between attempts (seconds)
        
    Returns:
        bool: True if the instance appears to be awake, False otherwise
    """
    logger.info(f"Attempting to wake up ServiceNow instance: {instance_url}")
    
    # Create a session to handle cookies and redirects
    session = requests.Session()
    
    for attempt in range(1, max_attempts + 1):
        logger.info(f"Wake-up attempt {attempt}/{max_attempts}...")
        
        try:
            # Make a request to the instance
            response = session.get(
                instance_url,
                allow_redirects=True,
                timeout=30
            )
            
            # Check if we got a JSON response from the API
            if "application/json" in response.headers.get("Content-Type", ""):
                logger.info("Instance appears to be awake (JSON response received)")
                return True
                
            # Check if we're still getting the hibernation page
            if "Instance Hibernating" in response.text:
                logger.info("Instance is still hibernating")
                
                # Look for the wake-up URL in the page
                if "wu=true" in response.text:
                    wake_url = "https://developer.servicenow.com/dev.do#!/home?wu=true"
                    logger.info(f"Following wake-up URL: {wake_url}")
                    
                    # Make a request to the wake-up URL
                    wake_response = session.get(wake_url, allow_redirects=True, timeout=30)
                    logger.info(f"Wake-up request status: {wake_response.status_code}")
            else:
                # Check if we got a login page or something else
                logger.info(f"Got response with status {response.status_code}, but not the hibernation page")
                logger.info(f"Content type: {response.headers.get('Content-Type')}")
                
            # Wait before the next attempt
            if attempt < max_attempts:
                logger.info(f"Waiting {wait_time} seconds before next attempt...")
                time.sleep(wait_time)
                
        except requests.RequestException as e:
            logger.error(f"Error during wake-up attempt: {e}")
            
            if attempt < max_attempts:
                logger.info(f"Waiting {wait_time} seconds before next attempt...")
                time.sleep(wait_time)
    
    logger.warning(f"Failed to wake up instance after {max_attempts} attempts")
    return False

def main():
    """Main function."""
    # Load environment variables
    load_dotenv()
    
    # Get ServiceNow instance URL
    instance_url = os.getenv("SERVICENOW_INSTANCE_URL")
    if not instance_url:
        logger.error("SERVICENOW_INSTANCE_URL environment variable is not set")
        sys.exit(1)
    
    # Try to wake up the instance
    success = wake_instance(instance_url)
    
    if success:
        logger.info("ServiceNow instance wake-up process completed successfully")
        sys.exit(0)
    else:
        logger.error("Failed to wake up ServiceNow instance")
        logger.info("You may need to manually wake up the instance by visiting:")
        logger.info("https://developer.servicenow.com/dev.do#!/home?wu=true")
        sys.exit(1)

if __name__ == "__main__":
    main() 
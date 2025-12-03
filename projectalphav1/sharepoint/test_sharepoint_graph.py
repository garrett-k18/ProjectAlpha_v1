"""
SharePoint Connection Test Using Microsoft Graph API
====================================================
This script tests SharePoint access using Microsoft Graph API with your existing permissions.

Requirements:
    pip install requests msal

Usage:
    python test_sharepoint_graph.py

Author: Project Alpha v1 Team
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)


def test_graph_sharepoint_connection():
    """
    Test SharePoint connection using Microsoft Graph API.
    Uses the Sites.Selected permission that's already configured in Azure AD.
    """
    
    print("=" * 80)
    print("SharePoint Connection Test (Microsoft Graph API)")
    print("=" * 80)
    
    # Step 1: Load credentials
    print("\n[1/5] Loading credentials from .env file...")
    
    client_id = os.getenv('SHAREPOINT_CLIENT_ID')
    client_secret = os.getenv('SHAREPOINT_CLIENT_SECRET')
    tenant_id = os.getenv('SHAREPOINT_TENANT_ID')
    
    if not all([client_id, client_secret, tenant_id]):
        print("❌ ERROR: Missing required credentials in .env file")
        return False
    
    print("✓ Credentials loaded successfully")
    print(f"   Client ID: {client_id[:8]}...{client_id[-4:]}")
    print(f"   Tenant ID: {tenant_id[:8]}...{tenant_id[-4:]}")
    
    # Step 2: Check for required library
    print("\n[2/5] Checking for required libraries...")
    
    try:
        import msal
        import requests
        print("✓ Required libraries found (msal, requests)")
    except ImportError as e:
        print(f"❌ ERROR: Missing library: {e}")
        print("\n   To install, run:")
        print("   pip install msal requests")
        return False
    
    # Step 3: Get SharePoint site information
    print("\n[3/5] SharePoint Site Information")
    print("   Please provide your SharePoint details.")
    print("   Example: firstliencapitaldom.sharepoint.com, site: ProjectAlpha")
    
    hostname_input = input("\n   Enter SharePoint hostname (e.g., firstliencapitaldom.sharepoint.com): ").strip()
    site_name = input("   Enter site name (e.g., ProjectAlpha) or press Enter for root: ").strip()
    
    if not hostname_input:
        print("❌ ERROR: Hostname is required")
        return False
    
    # Clean up hostname - remove protocol and path if user pasted full URL
    hostname = hostname_input
    hostname = hostname.replace('https://', '').replace('http://', '')
    # Remove any path (e.g., /sites/ProjectAlpha)
    if '/' in hostname:
        hostname = hostname.split('/')[0]
    
    print(f"✓ Hostname: {hostname}")
    if site_name:
        print(f"✓ Site name: {site_name}")
    
    # Step 4: Authenticate and get access token
    print("\n[4/5] Authenticating with Microsoft Graph...")
    
    try:
        # Create MSAL confidential client application
        authority = f"https://login.microsoftonline.com/{tenant_id}"
        app = msal.ConfidentialClientApplication(
            client_id,
            authority=authority,
            client_credential=client_secret,
        )
        
        # Get token for Microsoft Graph
        scopes = ["https://graph.microsoft.com/.default"]
        result = app.acquire_token_for_client(scopes=scopes)
        
        if "access_token" not in result:
            print("❌ ERROR: Failed to acquire access token")
            print(f"   Error: {result.get('error')}")
            print(f"   Description: {result.get('error_description')}")
            return False
        
        access_token = result["access_token"]
        print("✓ Access token acquired successfully")
        print(f"   Token preview: {access_token[:30]}...")
        
    except Exception as e:
        print(f"❌ ERROR: Authentication failed")
        print(f"   {type(e).__name__}: {str(e)}")
        return False
    
    # Step 5: Test SharePoint access via Graph API
    print("\n[5/5] Testing SharePoint access...")
    
    try:
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        
        # Test 1: Get site information
        if site_name:
            # Get specific site
            site_url = f"https://graph.microsoft.com/v1.0/sites/{hostname}:/sites/{site_name}"
        else:
            # Get root site
            site_url = f"https://graph.microsoft.com/v1.0/sites/{hostname}"
        
        print(f"\n   Testing site access: {site_url}")
        response = requests.get(site_url, headers=headers)
        
        if response.status_code == 200:
            site_data = response.json()
            print("\n✅ SUCCESS! SharePoint site accessible via Microsoft Graph")
            
            print("\n" + "=" * 80)
            print("SharePoint Site Information")
            print("=" * 80)
            print(f"Site Name: {site_data.get('displayName', 'N/A')}")
            print(f"Site ID: {site_data.get('id', 'N/A')}")
            print(f"Web URL: {site_data.get('webUrl', 'N/A')}")
            print(f"Description: {site_data.get('description', 'N/A')}")
            
            # Test 2: Try to list document libraries
            site_id = site_data.get('id')
            if site_id:
                print("\n" + "-" * 80)
                print("Document Libraries (Drives):")
                print("-" * 80)
                
                drives_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives"
                drives_response = requests.get(drives_url, headers=headers)
                
                if drives_response.status_code == 200:
                    drives_data = drives_response.json()
                    drives = drives_data.get('value', [])
                    
                    if drives:
                        for drive in drives:
                            name = drive.get('name', 'Unknown')
                            drive_type = drive.get('driveType', 'unknown')
                            web_url = drive.get('webUrl', 'N/A')
                            print(f"\n  📁 {name} ({drive_type})")
                            print(f"     URL: {web_url}")
                    else:
                        print("  No drives/libraries found")
                else:
                    print(f"  ⚠ Could not list drives (Status: {drives_response.status_code})")
            
            print("\n" + "=" * 80)
            print("✅ Connection Test SUCCESSFUL!")
            print("=" * 80)
            print("\n🎉 Your SharePoint credentials are working correctly with Microsoft Graph!")
            print(f"   You can access: https://{hostname}")
            
            return True
            
        elif response.status_code == 403:
            print(f"\n❌ ERROR: Access Denied (403)")
            print("\n   Your app has 'Sites.Selected' permission, which means:")
            print("   - You need to grant this specific app access to this specific site")
            print("   - This is done via SharePoint admin center or PowerShell")
            print("\n   SOLUTION OPTIONS:")
            print("\n   Option 1: Grant site-specific access (Recommended for Sites.Selected)")
            print("   Run this PowerShell command as SharePoint admin:")
            print(f"\n   Connect-PnPOnline -Url https://{hostname}/sites/{site_name} -Interactive")
            print(f"   Grant-PnPAzureADAppSitePermission -AppId '{client_id}' -DisplayName 'SharePoint API' -Permissions Write")
            print("\n   Option 2: Change permission to Sites.FullControl.All")
            print("   - Go to Azure AD > App registrations > API permissions")
            print("   - Remove Sites.Selected")
            print("   - Add Microsoft Graph > Application > Sites.FullControl.All")
            print("   - Grant admin consent")
            
            return False
            
        elif response.status_code == 404:
            print(f"\n❌ ERROR: Site Not Found (404)")
            print(f"\n   The site might not exist or the URL is incorrect:")
            print(f"   - Hostname: {hostname}")
            if site_name:
                print(f"   - Site name: {site_name}")
            print("\n   Try:")
            print("   1. Verify the site exists by opening it in a browser")
            print("   2. Check the exact site name (case-sensitive)")
            print("   3. Try without a site name (root site only)")
            
            return False
            
        else:
            print(f"\n❌ ERROR: Unexpected response (Status: {response.status_code})")
            print(f"   Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: Request failed")
        print(f"   {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point."""
    try:
        success = test_graph_sharepoint_connection()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠ Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()


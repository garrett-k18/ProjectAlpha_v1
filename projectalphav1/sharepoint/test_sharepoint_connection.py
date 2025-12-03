"""
SharePoint Connection Test Script
==================================
This script tests the SharePoint API connection using credentials from .env file.

Requirements:
    pip install Office365-REST-Python-Client

Usage:
    python test_sharepoint_connection.py

Author: Project Alpha v1 Team
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

def test_sharepoint_connection():
    """
    Test SharePoint connection using credentials from .env file.
    
    This function will:
    1. Load SharePoint credentials from environment variables
    2. Attempt to connect to your SharePoint site
    3. Retrieve basic site information to verify the connection
    4. Display results
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    
    print("=" * 80)
    print("SharePoint Connection Test")
    print("=" * 80)
    
    # Step 1: Load credentials from environment
    print("\n[1/5] Loading credentials from .env file...")
    
    # Get SharePoint credentials
    client_id = os.getenv('SHAREPOINT_CLIENT_ID')
    client_secret = os.getenv('SHAREPOINT_CLIENT_SECRET')
    tenant_id = os.getenv('SHAREPOINT_TENANT_ID')
    user_email = os.getenv('SHAREPOINT_USER_EMAIL')
    
    # Validate credentials
    if not all([client_id, client_secret, tenant_id]):
        print("❌ ERROR: Missing required SharePoint credentials in .env file")
        print("   Required variables:")
        print(f"   - SHAREPOINT_CLIENT_ID: {'✓' if client_id else '✗'}")
        print(f"   - SHAREPOINT_CLIENT_SECRET: {'✓' if client_secret else '✗'}")
        print(f"   - SHAREPOINT_TENANT_ID: {'✓' if tenant_id else '✗'}")
        return False
    
    print("✓ Credentials loaded successfully")
    print(f"   Client ID: {client_id[:8]}...{client_id[-4:]}")
    print(f"   Tenant ID: {tenant_id[:8]}...{tenant_id[-4:]}")
    print(f"   User Email: {user_email}")
    
    # Step 2: Get SharePoint site URL from user
    print("\n[2/5] SharePoint Site URL Required")
    print("   Please provide your SharePoint site URL.")
    print("   Format examples:")
    print("   - https://yourcompany.sharepoint.com/sites/yoursite")
    print("   - https://yourcompany.sharepoint.com")
    
    site_url = input("\n   Enter your SharePoint site URL: ").strip()
    
    if not site_url:
        print("❌ ERROR: No site URL provided")
        return False
    
    if not site_url.startswith('https://'):
        print("❌ ERROR: Site URL must start with https://")
        return False
    
    print(f"✓ Site URL: {site_url}")
    
    # Step 3: Check if Office365-REST-Python-Client is installed
    print("\n[3/5] Checking for required library...")
    
    try:
        from office365.sharepoint.client_context import ClientContext
        from office365.runtime.auth.client_credential import ClientCredential
        print("✓ Office365-REST-Python-Client library found")
    except ImportError:
        print("❌ ERROR: Office365-REST-Python-Client library not installed")
        print("\n   To install, run:")
        print("   pip install Office365-REST-Python-Client")
        print("\n   Or add to requirements.txt and run:")
        print("   pip install -r projectalphav1/requirements.txt")
        return False
    
    # Step 4: Attempt connection
    print("\n[4/5] Connecting to SharePoint...")
    
    try:
        # Create credentials object
        credentials = ClientCredential(client_id, client_secret)
        
        # Create context with credentials
        ctx = ClientContext(site_url).with_credentials(credentials)
        
        # Test connection by loading the web object
        web = ctx.web
        ctx.load(web)
        ctx.execute_query()
        
        print("✓ Successfully connected to SharePoint!")
        
    except Exception as e:
        print(f"❌ ERROR: Failed to connect to SharePoint")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        print("\n   Common issues:")
        print("   1. Client Secret may be incorrect (it looks like a GUID but should be a secret string)")
        print("   2. App registration needs proper API permissions in Azure AD:")
        print("      - SharePoint > Application permissions > Sites.FullControl.All")
        print("      - Or Sites.Selected with specific site permissions")
        print("   3. Admin consent may not be granted for the app")
        print("   4. The site URL may be incorrect")
        print("   5. The tenant ID may be incorrect")
        return False
    
    # Step 5: Display site information
    print("\n[5/5] Retrieving site information...")
    
    try:
        # Get site properties
        print("\n" + "=" * 80)
        print("SharePoint Site Information")
        print("=" * 80)
        print(f"Site URL: {web.url}")
        print(f"Site Title: {web.properties.get('Title', 'N/A')}")
        print(f"Web ID: {web.properties.get('Id', 'N/A')}")
        print(f"Description: {web.properties.get('Description', 'N/A')}")
        
        # Try to list document libraries
        print("\n" + "-" * 80)
        print("Document Libraries:")
        print("-" * 80)
        
        lists = ctx.web.lists
        ctx.load(lists)
        ctx.execute_query()
        
        doc_libs = [lst for lst in lists if lst.properties.get('BaseTemplate') == 101]
        
        if doc_libs:
            for lib in doc_libs:
                title = lib.properties.get('Title', 'Unknown')
                item_count = lib.properties.get('ItemCount', 0)
                print(f"  - {title} ({item_count} items)")
        else:
            print("  No document libraries found (or insufficient permissions)")
        
        print("\n" + "=" * 80)
        print("✅ Connection Test SUCCESSFUL!")
        print("=" * 80)
        print("\nYour SharePoint credentials are working correctly.")
        print(f"You can now use these credentials to access: {site_url}")
        
        return True
        
    except Exception as e:
        print(f"⚠ WARNING: Connected but couldn't retrieve all information")
        print(f"   Error: {str(e)}")
        print("\n   This might indicate limited permissions.")
        print("   Basic connection is working, but you may need additional permissions")
        print("   for full functionality.")
        return True


def main():
    """Main entry point for the test script."""
    try:
        success = test_sharepoint_connection()
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


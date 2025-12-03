"""
Grant Site-Specific Permission to Azure AD App
==============================================
This script grants your app access to ONLY the ProjectAlpha site using Microsoft Graph API.

Usage:
    python grant_site_permission.py
"""

import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)


def grant_site_permission():
    """Grant app permission to specific SharePoint site."""
    
    print("=" * 80)
    print("Grant Site Permission to Azure AD App")
    print("=" * 80)
    
    # Load credentials
    client_id = os.getenv('SHAREPOINT_CLIENT_ID')
    client_secret = os.getenv('SHAREPOINT_CLIENT_SECRET')
    tenant_id = os.getenv('SHAREPOINT_TENANT_ID')
    
    print("\n[1/4] Loading credentials...")
    print(f"✓ Client ID: {client_id[:8]}...{client_id[-4:]}")
    
    # Site info (hardcoded)
    print("\n[2/4] Site Information")
    hostname = "firstliencapitaldom.sharepoint.com"
    site_name = "ProjectAlpha"
    
    print(f"✓ Hostname: {hostname}")
    print(f"✓ Site: {site_name}")
    
    # Get access token
    print("\n[3/4] Getting access token...")
    try:
        import msal
        
        authority = f"https://login.microsoftonline.com/{tenant_id}"
        app = msal.ConfidentialClientApplication(
            client_id,
            authority=authority,
            client_credential=client_secret,
        )
        
        scopes = ["https://graph.microsoft.com/.default"]
        result = app.acquire_token_for_client(scopes=scopes)
        
        if "access_token" not in result:
            print(f"❌ ERROR: {result.get('error_description')}")
            return False
        
        access_token = result["access_token"]
        print("✓ Access token acquired")
        
    except ImportError:
        print("❌ ERROR: msal library not installed")
        print("   Run: pip install msal")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False
    
    # Get site ID
    print("\n[4/4] Granting site permission...")
    try:
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # First, get the site ID
        site_url = f"https://graph.microsoft.com/v1.0/sites/{hostname}:/sites/{site_name}"
        response = requests.get(site_url, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ ERROR: Could not find site (Status: {response.status_code})")
            print(f"   Response: {response.text}")
            return False
        
        site_data = response.json()
        site_id = site_data.get('id')
        print(f"✓ Found site ID: {site_id}")
        
        # Grant permission using Graph API
        permission_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/permissions"
        
        permission_data = {
            "roles": ["write"],
            "grantedToIdentities": [{
                "application": {
                    "id": client_id,
                    "displayName": "SharePoint API"
                }
            }]
        }
        
        perm_response = requests.post(permission_url, headers=headers, json=permission_data)
        
        if perm_response.status_code in [200, 201]:
            print("\n" + "=" * 80)
            print("✅ SUCCESS!")
            print("=" * 80)
            print(f"\nYour app now has access to ONLY:")
            print(f"  📁 Site: {site_data.get('displayName')}")
            print(f"  🔗 URL: {site_data.get('webUrl')}")
            print(f"\nPermission: Write (read + write)")
            print("\nTest your connection:")
            print("  python test_sharepoint_graph.py")
            return True
        else:
            print(f"⚠ WARNING: Could not grant permission automatically")
            print(f"   Status: {perm_response.status_code}")
            print(f"   Response: {perm_response.text}")
            print("\n" + "=" * 80)
            print("ALTERNATIVE: Use SharePoint Admin Center")
            print("=" * 80)
            print("\n1. Go to: https://firstliencapitaldom-admin.sharepoint.com/_layouts/15/appinv.aspx")
            print(f"2. Enter App ID: {client_id}")
            print("3. Click Lookup")
            print("4. In XML field, paste:")
            print(f"""
<AppPermissionRequests AllowAppOnlyPolicy="true">
  <AppPermissionRequest Scope="http://sharepoint/content/sitecollection/web" 
                       Right="Write" />
</AppPermissionRequests>
""")
            print("5. Click Create")
            print("6. Click Trust It")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    try:
        success = grant_site_permission()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(130)


if __name__ == '__main__':
    main()


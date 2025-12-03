"""
SharePoint Connection Diagnostic Tool
======================================
This script provides detailed diagnostics for SharePoint authentication issues.

Usage:
    python diagnose_sharepoint.py
"""

import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)


def test_azure_ad_token():
    """
    Test if we can get an access token from Azure AD.
    This is the first step in SharePoint authentication.
    """
    print("=" * 80)
    print("SharePoint Authentication Diagnostics")
    print("=" * 80)
    
    # Load credentials
    client_id = os.getenv('SHAREPOINT_CLIENT_ID')
    client_secret = os.getenv('SHAREPOINT_CLIENT_SECRET')
    tenant_id = os.getenv('SHAREPOINT_TENANT_ID')
    
    print("\n[Step 1] Checking credentials...")
    print(f"Client ID: {client_id}")
    print(f"Client Secret: {client_secret[:10]}...{client_secret[-4:]}")
    print(f"Tenant ID: {tenant_id}")
    
    # Get SharePoint domain
    print("\n[Step 2] SharePoint Site Information")
    sharepoint_domain = input("Enter your SharePoint domain (e.g., firstliencapitaldom): ").strip()
    site_path = input("Enter site path (e.g., /sites/ProjectAlpha) or press Enter for root: ").strip()
    
    if not site_path:
        site_url = f"https://{sharepoint_domain}.sharepoint.com"
    else:
        if not site_path.startswith('/'):
            site_path = '/' + site_path
        site_url = f"https://{sharepoint_domain}.sharepoint.com{site_path}"
    
    resource = f"https://{sharepoint_domain}.sharepoint.com"
    
    print(f"\nSite URL: {site_url}")
    print(f"Resource: {resource}")
    
    # Test Azure AD token endpoint
    print("\n[Step 3] Testing Azure AD Token Endpoint...")
    token_url = f"https://accounts.accesscontrol.windows.net/{tenant_id}/tokens/OAuth/2"
    
    token_data = {
        'grant_type': 'client_credentials',
        'client_id': f'{client_id}@{tenant_id}',
        'client_secret': client_secret,
        'resource': f'00000003-0000-0ff1-ce00-000000000000/{sharepoint_domain}.sharepoint.com@{tenant_id}'
    }
    
    print(f"Token URL: {token_url}")
    print(f"Client ID (formatted): {client_id}@{tenant_id}")
    print(f"Resource (formatted): 00000003-0000-0ff1-ce00-000000000000/{sharepoint_domain}.sharepoint.com@{tenant_id}")
    
    try:
        response = requests.post(token_url, data=token_data)
        
        if response.status_code == 200:
            print("\n✅ SUCCESS: Access token obtained!")
            token_response = response.json()
            access_token = token_response.get('access_token')
            print(f"Token preview: {access_token[:50]}...")
            
            # Test SharePoint API with token
            print("\n[Step 4] Testing SharePoint API Access...")
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json;odata=verbose'
            }
            
            api_url = f"{site_url}/_api/web"
            api_response = requests.get(api_url, headers=headers)
            
            if api_response.status_code == 200:
                print("✅ SUCCESS: SharePoint API accessible!")
                data = api_response.json()
                web_title = data.get('d', {}).get('Title', 'N/A')
                web_url = data.get('d', {}).get('Url', 'N/A')
                print(f"\nSite Title: {web_title}")
                print(f"Site URL: {web_url}")
                print("\n" + "=" * 80)
                print("✅ All diagnostics PASSED! Your credentials work correctly.")
                print("=" * 80)
                return True
            else:
                print(f"❌ ERROR: SharePoint API returned {api_response.status_code}")
                print(f"Response: {api_response.text[:500]}")
                return False
                
        else:
            print(f"\n❌ ERROR: Failed to get access token")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            print("\n" + "=" * 80)
            print("Troubleshooting Steps:")
            print("=" * 80)
            
            if response.status_code == 401:
                print("\n1. VERIFY APP REGISTRATION IN AZURE AD:")
                print("   - Go to: https://portal.azure.com")
                print("   - Navigate: Azure Active Directory > App registrations")
                print("   - Find your app (Client ID: {})".format(client_id))
                print("   - Verify the client secret is correct and not expired")
                
                print("\n2. CHECK API PERMISSIONS:")
                print("   - In your app registration, go to 'API permissions'")
                print("   - You need: SharePoint > Application permissions > Sites.FullControl.All")
                print("   - Make sure 'Grant admin consent' is clicked (green checkmark)")
                
                print("\n3. VERIFY APP-ONLY POLICY:")
                print("   - Your app must be registered for app-only access")
                print("   - The tenant ID must match your SharePoint tenant")
                
            elif response.status_code == 400:
                print("\n1. TENANT ID might be incorrect")
                print("   - Verify: Azure Active Directory > Overview > Tenant ID")
                print(f"   - Current: {tenant_id}")
                
                print("\n2. SHAREPOINT DOMAIN might be incorrect")
                print(f"   - Current: {sharepoint_domain}.sharepoint.com")
                print("   - Verify by opening your SharePoint site in a browser")
            
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point."""
    try:
        success = test_azure_ad_token()
        
        if not success:
            print("\n" + "=" * 80)
            print("RECOMMENDED NEXT STEPS:")
            print("=" * 80)
            print("\n1. Verify your Azure AD app registration:")
            print("   URL: https://portal.azure.com/#view/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/~/RegisteredApps")
            
            print("\n2. Check if your app has these permissions:")
            print("   - SharePoint > Application permissions > Sites.FullControl.All")
            print("   - Status: Admin consent granted ✓")
            
            print("\n3. Verify your app supports 'App-only' authentication:")
            print("   - This is required for client_credentials flow")
            
            print("\n4. Alternative: Try Microsoft Graph API instead:")
            print("   - Modern approach using your existing MICROSOFT_CLIENT_ID")
            print("   - May have better permission management")
            
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\nDiagnostics interrupted by user")
        sys.exit(130)


if __name__ == '__main__':
    main()


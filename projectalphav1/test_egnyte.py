"""
Quick test script to verify Egnyte API connection
"""
import django
import os

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projectalphav1.settings')
django.setup()

from core.services.serv_co_egnyteDoc import egnyte_service

print("\n" + "="*50)
print("EGNYTE API CONNECTION TEST")
print("="*50 + "\n")

# Test 1: List /Shared folder
print("Test 1: Listing /Shared folder...")
result = egnyte_service.list_folder('/Shared')

if result.get('success'):
    print("[SUCCESS] API is working!")
    print(f"\nAPI Response:")
    print(f"  - Success: {result['success']}")
    
    data = result.get('data', {})
    if 'folders' in data:
        print(f"  - Folders found: {len(data['folders'])}")
        if data['folders']:
            print(f"    First few folders: {[f.get('name') for f in data['folders'][:3]]}")
    
    if 'files' in data:
        print(f"  - Files found: {len(data['files'])}")
        if data['files']:
            print(f"    First few files: {[f.get('name') for f in data['files'][:3]]}")
    
    print(f"\n  - Full path: {data.get('path', 'N/A')}")
    print(f"  - Folder name: {data.get('name', 'N/A')}")
    
else:
    print("[FAILED] API connection error")
    print(f"Error: {result.get('error')}")
    print("\nPossible causes:")
    print("  1. API key not approved yet")
    print("  2. API key doesn't have required permissions")
    print("  3. Need to wait for API approval in Egnyte portal")

print("\n" + "="*50)
print("TEST COMPLETE")
print("="*50 + "\n")


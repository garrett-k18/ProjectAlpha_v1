# SharePoint Connection Test Instructions

## Overview
This guide helps you test your SharePoint API credentials to ensure they're configured correctly.

## Prerequisites

1. **SharePoint App Registration**: You must have an Azure AD app registered with:
   - Client ID (you have this ✓)
   - Client Secret (you have this ✓)
   - Tenant ID (you have this ✓)
   - Proper API permissions granted

2. **Required API Permissions in Azure AD**:
   - SharePoint > Application permissions > `Sites.FullControl.All`
   - OR `Sites.Selected` with specific site permissions
   - ⚠️ **Admin consent must be granted**

3. **SharePoint Site URL**: You need the URL of your test SharePoint site

## Setup Steps

### Step 1: Install Required Library

Activate your virtual environment and install the Office365 REST Python Client:

```powershell
# Activate virtual environment
& "B:\Garrett_Local_Share\ProjectAlpha_v1\.venv\Scripts\Activate.ps1"

# Install the library
pip install Office365-REST-Python-Client

# Or install all updated requirements
pip install -r projectalphav1/requirements.txt
```

### Step 2: Run the Test Script

```powershell
# Make sure you're in the project root directory
cd B:\Garrett_Local_Share\ProjectAlpha_v1

# Run the test script
python test_sharepoint_connection.py
```

### Step 3: Provide SharePoint Site URL

When prompted, enter your SharePoint site URL. Examples:
- `https://firstliencapital.sharepoint.com/sites/yoursite`
- `https://firstliencapital.sharepoint.com`

## Expected Output

If successful, you should see:
- ✓ Credentials loaded successfully
- ✓ Successfully connected to SharePoint!
- Site information (URL, Title, Description)
- List of document libraries (if permissions allow)
- ✅ Connection Test SUCCESSFUL!

## Troubleshooting

### Common Issues

#### 1. "Client Secret may be incorrect"
**Problem**: Your `SHAREPOINT_CLIENT_SECRET` looks like a GUID, but it should be a secret string.

**Solution**: 
- Go to Azure Portal > App registrations > Your app
- Navigate to "Certificates & secrets"
- Create a new client secret
- Copy the **Value** (not the Secret ID) to your `.env` file

#### 2. "Access denied" or "Unauthorized"
**Problem**: App doesn't have proper permissions.

**Solution**:
- Go to Azure Portal > App registrations > Your app > API permissions
- Add: SharePoint > Application permissions > Sites.FullControl.All
- Click "Grant admin consent for [Your Organization]"

#### 3. "Tenant not found"
**Problem**: Incorrect Tenant ID.

**Solution**:
- Verify your tenant ID in Azure Portal > Azure Active Directory > Overview
- Update `SHAREPOINT_TENANT_ID` in `.env` file

#### 4. "Site not found"
**Problem**: Incorrect SharePoint site URL.

**Solution**:
- Verify the URL by opening it in your browser
- Ensure you have access to the site
- Use the full URL including protocol (https://)

## Credentials Location

Your SharePoint credentials are stored in:
```
B:\Garrett_Local_Share\ProjectAlpha_v1\.env
```

Current credentials (from `.env`):
- `SHAREPOINT_CLIENT_ID`: e5ab0597-80c3-417a-8b9d-75dbe5c7b5c7
- `SHAREPOINT_CLIENT_SECRET`: a19f312a-e16a-4219-b18a-150f54a15e35 ⚠️ (verify this is correct)
- `SHAREPOINT_TENANT_ID`: 482bada8-8a8b-47a9-b124-752123da321f
- `SHAREPOINT_USER_EMAIL`: garrett@firstliencapital.com

## Next Steps

Once the connection test is successful, you can:
1. Integrate SharePoint document retrieval into your Django app
2. Implement document upload functionality
3. Create automated document processing pipelines

## Documentation Links

- [Office365-REST-Python-Client GitHub](https://github.com/vgrem/office365-rest-python-client)
- [Azure App Registration Guide](https://learn.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app)
- [SharePoint REST API](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/get-to-know-the-sharepoint-rest-service)


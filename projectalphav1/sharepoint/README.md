# SharePoint Integration Module

## Overview

SharePoint integration for ProjectAlpha. Provides seamless document management with SharePoint as storage backend while maintaining Django as source of truth.

**Strategy:** Option 1 (Eager Creation)
- Folders created when trades/assets created
- SharePoint mirrors database structure
- Users upload via platform only
- SharePoint is read-only view for users

## Architecture

```
Platform (Django) ──writes──> SharePoint
      ↑                            ↓
    Source of Truth            Read-Only View
                                (for users)
```

## Folder Structure

```
/Trades/
  TRD-2024-001/
    /Bid/               ← Trade-level docs
    /Legal/
    /Post Close/
    /Assets/
      ASSET-12345/      ← Asset-level docs
        /Valuation/
        /Collateral/
        /Legal/
        /Tax/
        /Title/
        /Photos/
```

**Rule:** Files MUST be in category folders. No loose files at root.

## What's Been Created

### ✅ Models
- `model_sp_document.py` - Tracks files in database
  - Links to trades/assets
  - Stores SharePoint metadata
  - Audit trail (who, when)
  - Validation status

### ✅ Services
- `serv_sp_client.py` - Microsoft Graph API client
  - Authentication
  - Folder creation
  - File operations
  
- `serv_sp_folder_structure.py` - Folder hierarchy logic
  - Path generation
  - Structure definitions
  - Validation rules

### ✅ Management Commands
- `init_sharepoint_folders.py` - Initialize base structure
  ```bash
  python manage.py init_sharepoint_folders                    # Base structure
  python manage.py init_sharepoint_folders --trade TRD-001    # Trade folders
  python manage.py init_sharepoint_folders --dry-run          # Preview only
  ```

### ✅ Signals (Template)
- `signals.py` - Auto-create folders on entity save
  - Currently commented out
  - Ready to connect to your models

### ✅ Configuration
- Added to `INSTALLED_APPS`
- SharePoint settings in `settings.py`
- Credentials from `.env`

## Next Steps

### 1. Run Migrations

```bash
python manage.py makemigrations sharepoint
python manage.py migrate sharepoint
```

### 2. Test Connection

```bash
python manage.py init_sharepoint_folders --dry-run
```

Should show:
```
✓ Connected to: ProjectAlpha
  URL: https://firstliencapitaldom.sharepoint.com/sites/ProjectAlpha
```

### 3. Create Base Structure

```bash
python manage.py init_sharepoint_folders
```

Creates `/Trades` folder in SharePoint.

### 4. Connect to Your Models

Update `signals.py`:
1. Import your Trade/Asset models from `acq_module`
2. Uncomment signal receivers
3. Update field names to match your models
4. Add `sharepoint_folder_path` field to Trade/Asset models

Example:
```python
# In acq_module/models/your_trade_model.py
sharepoint_folder_path = models.CharField(max_length=512, blank=True)
```

### 5. Create Upload API

Need to create:
- `api/view_sp_upload.py` - File upload endpoint
- `services/serv_sp_upload.py` - Upload logic
- `services/serv_sp_validation.py` - File validation

### 6. Vue Frontend Component

Create upload component:
- File picker
- Category selector (dropdown of valid folders)
- Progress indicator
- Link to SharePoint view

## Validation Rules

### File Names
- Max 256 characters
- No forbidden chars: `~ # % & * { } \ : < > ? / | "`
- No leading/trailing spaces or periods

### File Paths
- ❌ `/Trades/TRD-001/file.pdf` - NOT ALLOWED (root)
- ✅ `/Trades/TRD-001/Legal/file.pdf` - OK (category folder)

### Folder Structure
- Trade IDs: `TRD-YYYY-NNN` format
- Asset IDs: Your format
- Fixed category folders (no custom folders)

## Permissions

**SharePoint Site:**
- Regular users: **Read only**
- App (your credentials): **Write** ✅
- Enforced: Users cannot upload directly to SharePoint

**Platform:**
- All uploads through Django API
- Validation before upload
- Audit trail in database

## Troubleshooting

### Can't connect to SharePoint
1. Check credentials in `.env`
2. Verify admin granted site access (Sites.Selected)
3. Run test: `python test_sharepoint_graph.py`

### Folders not creating
1. Check logs: `python manage.py shell` then test client
2. Verify permissions (app needs Write)
3. Check path format (no special chars)

### Files not syncing
1. Check SharePointDocument records in DB
2. Verify `sharepoint_item_id` stored
3. Check logs for errors

## Security Notes

- Credentials in `.env` (never commit!)
- Production: Use environment variables
- SharePoint: Read-only for users enforced at SharePoint level
- Audit trail: All uploads logged with user/timestamp
- Soft deletes: Files archived, not permanently deleted

## Development Workflow

```bash
# 1. Make changes to models/services
# 2. Create migrations
python manage.py makemigrations sharepoint

# 3. Apply migrations  
python manage.py migrate sharepoint

# 4. Test folder creation
python manage.py init_sharepoint_folders --trade TEST-001

# 5. Check SharePoint
# Open: https://firstliencapitaldom.sharepoint.com/sites/ProjectAlpha
```

## API Usage Examples

### Create Trade (triggers folder creation)
```python
# Your view creates trade
trade = Trade.objects.create(
    trade_id="TRD-2024-001",
    # ... other fields
)
# Signal automatically creates SharePoint folders
```

### Upload File (future)
```python
# Will be implemented in view_sp_upload.py
POST /api/sharepoint/upload/
{
    "trade_id": "TRD-2024-001",
    "asset_id": "ASSET-12345",  # optional
    "category": "asset_valuation",
    "file": <file_upload>
}
```

## Questions?

See test script: `test_sharepoint_graph.py`
See credentials: `.env`



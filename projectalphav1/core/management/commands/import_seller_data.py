"""
Django Management Command Wrapper for Seller Data ETL Import.

WHAT: Lightweight wrapper that delegates to the actual ETL command in a subdirectory.
WHY: Django's management command discovery ONLY works for files directly in management/commands/.
     It does NOT search subdirectories, even with __init__.py files.
WHERE: This wrapper lives in core/management/commands/ (where Django looks).
       Actual implementation is in prod_import_scripts/data_tape/import_seller_data.py.
HOW: Dynamically imports the Command class from subdirectory and re-exports it for Django.

PROBLEM WE'RE SOLVING:
- We want organized code structure: prod_import_scripts/data_tape/ for production ETL scripts
- Django requires commands directly in management/commands/ folder
- Solution: Small wrapper here, full implementation in organized subdirectory

BENEFITS:
- ✅ Keeps production scripts organized by type (data_tape, bpo, etc.)
- ✅ Co-locates documentation with implementation (README, INSTRUCTIONS, examples)
- ✅ Django still discovers the command via this wrapper
- ✅ No code duplication - wrapper is ~30 lines, implementation is 700+ lines

DOCUMENTATION:
Full documentation is co-located with the actual implementation:
- prod_import_scripts/data_tape/README_ETL.md - Quick reference guide
- prod_import_scripts/data_tape/ETL_INSTRUCTIONS.md - Comprehensive usage guide
- prod_import_scripts/data_tape/QUICK_TEST.md - Step-by-step testing walkthrough
- prod_import_scripts/data_tape/example_mapping_config.json - Template configuration

USAGE:
    python manage.py import_seller_data --file data.xlsx --seller-name "ABC" --auto-create
    
See documentation files above for complete usage examples.
"""

import sys
from pathlib import Path

# WHAT: Add subdirectory to Python's import path
# WHY: Allows us to import the Command class from prod_import_scripts/data_tape/
# HOW: Temporarily adds the subdirectory path so Python can find the module
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / 'prod_import_scripts' / 'data_tape'))

# WHAT: Import the actual Command class from subdirectory implementation
# WHY: Django expects a 'Command' class in this file to execute the management command
# HOW: Import statement pulls in the full Command class definition from subdirectory
from import_seller_data import Command

# WHAT: Explicitly declare what this module exports
# WHY: Makes it clear to Django (and developers) that Command is the public interface
# HOW: __all__ list controls what gets imported when someone does "from module import *"
__all__ = ['Command']

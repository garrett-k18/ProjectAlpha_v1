"""
Django Admin Organization Guide

This document explains how to organize Django admin models into folders/hierarchy.

OPTION 1: CODE ORGANIZATION (Recommended for maintainability)
============================================================

Convert admin.py into an admin/ folder structure:

1. Create admin/ directory:
   projectalphav1/core/admin/
   
2. Create __init__.py that imports all admin classes:
   # All admin classes imported here for auto-discovery
   from .capital_admin import *
   from .crm_admin import *
   from .assumptions_admin import *

3. Split admin.py into logical files:
   - capital_admin.py: DebtFacility, CoInvestor, Fund, etc.
   - crm_admin.py: MasterCRM
   - assumptions_admin.py: StateReference, Servicer, FCStatus, etc.
   - assets_admin.py: AssetIdHub, Valuation, Photo, Document
   - transactions_admin.py: LLTransactionSummary, LLCashFlowSeries
   - commercial_admin.py: UnitMix, RentRoll, ComparableProperty

Benefits:
- Better code organization
- Easier to maintain
- Logical grouping of related models
- Django still auto-discovers all admin classes

OPTION 2: VISUAL UI ORGANIZATION (Using admin_interface package)
==================================================================

You already have 'admin_interface' installed! Use it to customize the admin UI.

1. Run migrations (if not already done):
   python manage.py migrate admin_interface colorfield

2. Customize admin interface in Django admin:
   - Go to /admin/admin_interface/theme/
   - Create/edit theme settings
   - Organize models by changing app order

3. For programmatic organization, customize admin site:
   See custom_admin_site.py for example

OPTION 3: CUSTOM ADMIN SITE (Advanced)
======================================

Create a custom AdminSite class that groups models visually.

See: core/admin/custom_admin_site.py

To use:
1. Update settings.py:
   INSTALLED_APPS = [
       ...
       'core.admin.custom_admin_site.CustomAdminConfig',  # Replace django.contrib.admin
   ]

2. Update urls.py:
   from core.admin.custom_admin_site import custom_admin_site
   urlpatterns = [
       path('admin/', custom_admin_site.urls),
   ]

RECOMMENDED APPROACH
====================

For your codebase, I recommend:
1. Use OPTION 1 (folder structure) for code organization
2. Use OPTION 2 (admin_interface) for visual UI customization

This gives you both maintainable code AND a better admin interface.
"""

# Example of how to organize admin files:

# core/admin/__init__.py
"""
from .capital_admin import *
from .crm_admin import *
from .assumptions_admin import *
from .assets_admin import *
from .transactions_admin import *
from .commercial_admin import *
"""

# core/admin/capital_admin.py
"""
from django.contrib import admin
from core.models import DebtFacility, CoInvestor, Fund

@admin.register(DebtFacility)
class DebtFacilityAdmin(admin.ModelAdmin):
    # ... your admin config
"""

# And so on for each logical group...


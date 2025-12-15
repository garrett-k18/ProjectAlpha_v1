"""Display all fields being requested from Gemini extraction."""

import os
import sys
from pathlib import Path

if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projectalphav1.settings")
    import django
    django.setup()

from etl.models import ValuationETL, ComparablesETL, RepairItem
from etl.services.services_valuationExtract.serv_etl_valuation_vision_extractor import _SKIP_FIELD_NAMES

# Use the actual skip list from the vision extractor
SKIP = _SKIP_FIELD_NAMES

def show_model_fields(model, title):
    """Display all fields for a model."""
    print("\n" + "=" * 80)
    print(f"{title}")
    print("=" * 80)
    
    fields = []
    for field in model._meta.get_fields():
        if getattr(field, "auto_created", False):
            continue
        if not getattr(field, "concrete", False):
            continue
        if field.name in SKIP:
            continue
        
        # Get field type
        field_type = field.__class__.__name__
        required = "REQUIRED" if not field.blank and not field.null and not hasattr(field, 'default') else "optional"
        
        fields.append((field.name, field_type, required))
    
    # Sort by name
    fields.sort()
    
    # Print
    for i, (name, ftype, req) in enumerate(fields, 1):
        print(f"{i:3d}. {name:50s} [{ftype:20s}] {req}")
    
    print(f"\nTotal: {len(fields)} fields")
    return len(fields)

# Show all models
total = 0
total += show_model_fields(ValuationETL, "VALUATION ETL FIELDS (Main valuation data)")
total += show_model_fields(ComparablesETL, "COMPARABLES ETL FIELDS (Comparable properties - arrays)")
total += show_model_fields(RepairItem, "REPAIR ITEM FIELDS (Repair items - arrays)")

print("\n" + "=" * 80)
print(f"TOTAL FIELDS REQUESTED FROM GEMINI: {total}")
print("=" * 80)

print("\n[TIP] TO REDUCE EXTRACTION TIME:")
print("      1. Remove optional/rarely-used fields from models")
print("      2. Use quick_extract() for just 15 critical fields")
print("      3. Use smart_extract() to validate before full extraction")

print("\n[CRITICAL] Fields to always keep:")
critical = [
    "property_address", "city", "state", "zip_code",
    "living_area", "bedrooms", "bathrooms", "year_built",
    "as_is_value", "as_repaired_value", "inspection_date",
    "condition", "occupancy_status"
]
for field in critical:
    print(f"           - {field}")

print("\n[REMOVED] Fields currently excluded from extraction:")
print(f"          Total: {len(SKIP)} fields")
for field in sorted(SKIP):
    if field not in {"id", "asset_hub", "valuation", "document", "original_document", "created_at", "updated_at", "created_by"}:
        print(f"           - {field}")


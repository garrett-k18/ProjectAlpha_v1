"""Test multi-pass extraction that bypasses 120-second timeout."""

import os
import sys
import time
from pathlib import Path

if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projectalphav1.settings")
    import django
    django.setup()

from etl.services import multipass_extract

# Get PDF path
pdf_path = sys.argv[1] if len(sys.argv) > 1 else "C:\\Users\\garre\\Documents\\2004954286.Pdf"

print("=" * 80)
print("MULTI-PASS EXTRACTION TEST")
print("(Bypasses 120-second server timeout by splitting into 4 passes)")
print("=" * 80)
print(f"File: {pdf_path}\n")

# Run extraction
print("Starting extraction...")
print("This will make 4 separate API calls, each under 120 seconds:")
print("  Pass 1: Core property/valuation data")
print("  Pass 2: Comparables")
print("  Pass 3: Market analysis")
print("  Pass 4: Repairs")
print()

start = time.time()
result = multipass_extract(pdf_path)
total_time = time.time() - start

print("\n" + "=" * 80)
print("RESULTS")
print("=" * 80)
print(f"Total time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
print(f"Valuation fields: {len(result.valuation_payload)}")
print(f"Comparables: {len(result.comparables_payload)}")
print(f"Repairs: {len(result.repairs_payload)}")
print()

# Show sample data
if result.valuation_payload:
    print("Sample valuation data:")
    print(f"  Address: {result.valuation_payload.get('property_address')}")
    print(f"  City: {result.valuation_payload.get('city')}, {result.valuation_payload.get('state')}")
    print(f"  As-Is Value: ${result.valuation_payload.get('as_is_value')}")
    print(f"  Repaired Value: ${result.valuation_payload.get('as_repaired_value')}")
    print(f"  Living Area: {result.valuation_payload.get('living_area')} sq ft")
    print(f"  Bed/Bath: {result.valuation_payload.get('bedrooms')}/{result.valuation_payload.get('bathrooms')}")

if result.comparables_payload:
    print(f"\nFirst comparable:")
    comp = result.comparables_payload[0]
    print(f"  Address: {comp.get('address')}")
    print(f"  Sale Price: ${comp.get('sale_price')}")
    print(f"  Distance: {comp.get('proximity_miles')} miles")

if result.repairs_payload:
    print(f"\nFirst repair:")
    repair = result.repairs_payload[0]
    print(f"  Type: {repair.get('repair_type')}")
    print(f"  Cost: ${repair.get('estimated_cost')}")

print("\n" + "=" * 80)
print("[SUCCESS] Multi-pass extraction completed!")
print("=" * 80)


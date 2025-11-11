"""Performance comparison: Fast vs Full extraction."""

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

from etl.services.serv_etl_gemini_optimized import OptimizedGeminiExtractor
from etl.services import GeminiVisionExtractionService

# Get PDF path
pdf_path = sys.argv[1] if len(sys.argv) > 1 else "C:\\Users\\garre\\Documents\\2004954286.Pdf"
print(f"Testing: {pdf_path}\n")

extractor = OptimizedGeminiExtractor()

# TEST 1: FAST EXTRACTION
print("=" * 80)
print("TEST 1: FAST EXTRACTION (15 key fields)")
print("=" * 80)
start = time.time()
fast_result = extractor.fast_extract(Path(pdf_path))
fast_time = time.time() - start

print(f"⏱️  Time: {fast_time:.1f} seconds")
print(f"📊 Fields extracted: {len([v for v in fast_result.values() if v is not None])}")
print(f"\n✅ Key Data:")
print(f"   Address: {fast_result.get('property_address')}")
print(f"   City: {fast_result.get('city')}, {fast_result.get('state')}")
print(f"   Sq Ft: {fast_result.get('living_area')}")
print(f"   Bed/Bath: {fast_result.get('bedrooms')}/{fast_result.get('bathrooms')}")
print(f"   As-Is Value: ${fast_result.get('as_is_value')}")
print(f"   Repaired Value: ${fast_result.get('repaired_value')}")

# TEST 2: OPTIMIZED FULL EXTRACTION
print("\n" + "=" * 80)
print("TEST 2: OPTIMIZED FULL EXTRACTION (150+ fields, minimal prompt)")
print("=" * 80)
start = time.time()
# Using the newly optimized prompt (minimal mode)
service = GeminiVisionExtractionService()
full_result = service.process(Path(pdf_path))
full_time = time.time() - start

print(f"⏱️  Time: {full_time:.1f} seconds")
print(f"📊 Fields extracted: {len(full_result.fields)}")
print(f"📍 Valuation fields: {len(full_result.valuation_payload)}")
print(f"🏘️  Comparables: {len(full_result.comparables_payload)}")
print(f"🔧 Repairs: {len(full_result.repairs_payload)}")
if full_result.warnings:
    print(f"⚠️  Warnings: {len(full_result.warnings)}")

# COMPARISON
print("\n" + "=" * 80)
print("PERFORMANCE COMPARISON")
print("=" * 80)
print(f"Fast Extraction:  {fast_time:6.1f}s ({len([v for v in fast_result.values() if v is not None])} fields)")
print(f"Full Extraction:  {full_time:6.1f}s ({len(full_result.fields)} fields)")
print(f"Speed Improvement: {(full_time/fast_time):.1f}x faster for fast mode")
print(f"Time Saved:        {(full_time-fast_time):.1f} seconds")

# RECOMMENDATION
print("\n" + "=" * 80)
print("RECOMMENDATIONS")
print("=" * 80)
print("✅ Use FAST mode when:")
print("   - Quick preview needed")
print("   - Validating document before full extraction")
print("   - Only need key valuation data")
print("   - Batch processing many documents")
print()
print("✅ Use FULL mode when:")
print("   - Need complete data for database")
print("   - Need comparables and repairs")
print("   - After fast mode validation passes")
print()
print("✅ Use SMART mode (automatic):")
print("   - Runs fast first to validate")
print("   - Only does full if document is valid")
print("   - Best for production workflows")


"""Run the production ETL pipeline to extract and save valuation data."""

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

from core.models import AssetIdHub
from etl.services.serv_etl_valuationPipeline import ValuationExtractionPipeline
from etl.services.serv_etl_gemini_multipass import MultiPassGeminiExtractor

# Get PDF path
pdf_path = sys.argv[1] if len(sys.argv) > 1 else "C:\\Users\\garre\\Documents\\2004954286.Pdf"

print("=" * 80)
print("PRODUCTION ETL PIPELINE")
print("=" * 80)
print(f"File: {pdf_path}\n")

# Create or get asset hub (required by pipeline)
# Just get the first one or create if none exists
asset_hub = AssetIdHub.objects.first()
if not asset_hub:
    asset_hub = AssetIdHub.objects.create(sellertape_id="TEST-ETL-001", servicer_id="TEST-ETL-001")
    print(f"Asset Hub ID: {asset_hub.id} (created)")
else:
    print(f"Asset Hub ID: {asset_hub.id} (existing)")

# Run pipeline with multipass extractor (bypasses 120s timeout)
print("\nRunning extraction pipeline with multi-pass extractor...")
print("(4 API calls, each under 120 seconds)")
start = time.time()

multipass_extractor = MultiPassGeminiExtractor()
pipeline = ValuationExtractionPipeline(extractor=multipass_extractor)
result = pipeline.process_document(
    file_path=Path(pdf_path),
    asset_hub=asset_hub,
    source="BPO"
)

total_time = time.time() - start

print("\n" + "=" * 80)
print("RESULTS")
print("=" * 80)
print(f"Total time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
print(f"Document ID: {result.document.id}")
print(f"Status: {result.document.status}")

if result.valuation:
    print(f"\n✅ Valuation saved (ID: {result.valuation.id})")
    print(f"   Address: {result.valuation.property_address}")
    print(f"   City: {result.valuation.city}, {result.valuation.state}")
    print(f"   As-Is Value: ${result.valuation.as_is_value}")
    print(f"   Repaired Value: ${result.valuation.as_repaired_value}")
    
    comp_count = result.valuation.comparables.count()
    repair_count = result.valuation.repairs.count()
    print(f"   Comparables: {comp_count}")
    print(f"   Repairs: {repair_count}")
else:
    print("\n❌ No valuation saved")

if result.warnings:
    print(f"\n⚠️  Warnings:")
    for warning in result.warnings:
        print(f"   - {warning}")

print("\n" + "=" * 80)
print("✅ ETL PIPELINE COMPLETE!")
print("=" * 80)


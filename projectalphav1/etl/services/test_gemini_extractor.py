"""Quick test script for Gemini Vision Extractor.

This script helps verify that the Gemini API is configured correctly and can
process documents. Run this after installing dependencies and setting up the
GEMINI_API_KEY environment variable.

Usage:
    python projectalphav1/etl/services/test_gemini_extractor.py /path/to/document.pdf
"""

import os
import sys
from pathlib import Path

# Django setup for standalone script
if __name__ == "__main__":
    # Add the project root to the Python path
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root))
    
    # Setup Django settings
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projectalphav1.settings")
    
    import django
    django.setup()

from etl.services.serv_etl_gemini_client import build_valuation_gemini_vision_client
from etl.services.serv_etl_valuation_vision_extractor import GeminiVisionExtractionService


def test_gemini_client():
    """Test that the Gemini client can be built successfully."""
    print("=" * 80)
    print("Testing Gemini Client Configuration")
    print("=" * 80)
    
    # Check if API key is set
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("[ERROR] GEMINI_API_KEY is not set in environment")
        print("        Please add it to your .env file")
        return False
    
    print(f"[OK] GEMINI_API_KEY is set (length: {len(api_key)})")
    
    # Try to build the client
    try:
        client = build_valuation_gemini_vision_client()
        if client is None:
            print("[ERROR] Failed to build Gemini client")
            return False
        print("[OK] Gemini client built successfully")
        return True
    except Exception as exc:
        print(f"[ERROR] Exception while building client: {exc}")
        return False


def test_gemini_extraction(file_path: str):
    """Test document extraction with Gemini."""
    print("\n" + "=" * 80)
    print("Testing Gemini Document Extraction")
    print("=" * 80)
    
    # Validate file path
    path = Path(file_path)
    if not path.exists():
        print(f"[ERROR] File not found: {file_path}")
        return False
    
    print(f"[OK] Document found: {path.name}")
    print(f"     Size: {path.stat().st_size:,} bytes")
    
    # Create the extraction service
    try:
        service = GeminiVisionExtractionService()
        print("[OK] GeminiVisionExtractionService created")
    except Exception as exc:
        print(f"[ERROR] Failed to create service: {exc}")
        return False
    
    # Process the document
    print("\nProcessing document...")
    try:
        result = service.process(path)
        print("[OK] Document processed successfully")
        
        # Display results
        print("\n" + "-" * 80)
        print("EXTRACTION RESULTS")
        print("-" * 80)
        print(f"Extracted at: {result.extracted_at}")
        print(f"MIME type: {result.mime_type}")
        print(f"Number of fields extracted: {len(result.fields)}")
        
        # Valuation data
        print(f"\nValuation fields: {len(result.valuation_payload)}")
        if result.valuation_payload:
            print("  Sample fields:")
            for key, value in list(result.valuation_payload.items())[:5]:
                print(f"    - {key}: {value}")
        
        # Comparables
        print(f"\nComparables: {len(result.comparables_payload)}")
        if result.comparables_payload:
            print(f"  First comparable has {len(result.comparables_payload[0])} fields")
        
        # Repairs
        print(f"\nRepair items: {len(result.repairs_payload)}")
        if result.repairs_payload:
            print(f"  First repair has {len(result.repairs_payload[0])} fields")
        
        # Warnings
        if result.warnings:
            print(f"\n[WARNING] Found {len(result.warnings)} warning(s):")
            for warning in result.warnings:
                print(f"          - {warning}")
        else:
            print("\n[OK] No warnings")
        
        # Inferred source
        if result.inferred_source:
            print(f"\nInferred source: {result.inferred_source}")
        
        # DEBUG: Show first chunk raw response
        if result.raw_response.get('chunks'):
            import json
            first_chunk = result.raw_response['chunks'][0]
            print("\n" + "-" * 80)
            print("DEBUG: First Chunk Raw Response")
            print("-" * 80)
            print(json.dumps(first_chunk, indent=2, default=str)[:2000])
            print("-" * 80)
        
        print("\n" + "=" * 80)
        print("[SUCCESS] TEST PASSED: Document extraction successful")
        print("=" * 80)
        return True
        
    except Exception as exc:
        print(f"\n[ERROR] Exception during extraction: {exc}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function."""
    print("\n")
    print("=" * 80)
    print("=" + " " * 20 + "GEMINI VISION EXTRACTOR TEST" + " " * 30 + "=")
    print("=" * 80)
    print()
    
    # Test 1: Client configuration
    if not test_gemini_client():
        print("\n[FAILED] Client configuration test failed")
        sys.exit(1)
    
    # Test 2: Document extraction (if file path provided)
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if not test_gemini_extraction(file_path):
            print("\n[FAILED] Document extraction test failed")
            sys.exit(1)
    else:
        print("\n" + "=" * 80)
        print("SKIPPING DOCUMENT EXTRACTION TEST")
        print("=" * 80)
        print("No document path provided.")
        print(f"Usage: python {sys.argv[0]} /path/to/document.pdf")
        print("=" * 80)
    
    print("\n[SUCCESS] ALL TESTS PASSED\n")


if __name__ == "__main__":
    main()


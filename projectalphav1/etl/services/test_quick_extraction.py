"""Quick extraction test with just a few fields."""

import os
import sys
from pathlib import Path

if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projectalphav1.settings")
    import django
    django.setup()

import google.generativeai as genai
import json

# Configure
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Get PDF
pdf_path = sys.argv[1] if len(sys.argv) > 1 else "C:\\Users\\garre\\Documents\\2004954286.Pdf"
print(f"[OK] Testing: {pdf_path}")

# Upload
uploaded_file = genai.upload_file(path=pdf_path, mime_type="application/pdf")
print(f"[OK] Uploaded: {uploaded_file.name}")

# Simple extraction prompt - just key fields
prompt = """
Read this valuation/appraisal document and extract the following fields.
Return ONLY JSON with this structure:

{
  "property_address": "...",
  "city": "...",
  "state": "...",
  "living_area": 0,
  "bedrooms": 0,
  "bathrooms": 0,
  "year_built": 0,
  "as_is_value": 0,
  "repaired_value": 0
}

Use null for missing fields. Return ONLY the JSON, no other text.
"""

# Generate
print("[PROCESSING] Extracting...")
model = genai.GenerativeModel(model_name="gemini-2.5-flash")
response = model.generate_content([uploaded_file, prompt])

print("\n" + "=" * 80)
print("EXTRACTION RESULT:")
print("=" * 80)
print(response.text)
print("=" * 80)

# Parse to verify it's valid JSON
try:
    data = json.loads(response.text)
    print(f"\n[OK] Valid JSON with {len(data)} fields")
    for key, value in data.items():
        print(f"  {key}: {value}")
except:
    print("[ERROR] Not valid JSON")

# Cleanup
genai.delete_file(uploaded_file.name)


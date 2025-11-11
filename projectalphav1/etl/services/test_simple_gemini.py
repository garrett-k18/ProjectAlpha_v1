"""Simple test to verify Gemini can read a PDF document."""

import os
import sys
from pathlib import Path

# Django setup for standalone script
if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projectalphav1.settings")
    
    import django
    django.setup()

import google.generativeai as genai

# Get API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("[ERROR] GEMINI_API_KEY not set")
    sys.exit(1)

print(f"[OK] API Key found: {api_key[:10]}...")

# Configure Gemini
genai.configure(api_key=api_key)

# Get the PDF file path
if len(sys.argv) < 2:
    print("Usage: python test_simple_gemini.py path/to/document.pdf")
    sys.exit(1)

pdf_path = sys.argv[1]
if not Path(pdf_path).exists():
    print(f"[ERROR] File not found: {pdf_path}")
    sys.exit(1)

print(f"[OK] File found: {pdf_path}")
print(f"     Size: {Path(pdf_path).stat().st_size:,} bytes")

# Upload the file
print("\n[UPLOADING] Uploading file to Gemini...")
uploaded_file = genai.upload_file(path=pdf_path, mime_type="application/pdf")
print(f"[OK] File uploaded: {uploaded_file.name}")
print(f"     MIME type: {uploaded_file.mime_type}")
print(f"     State: {uploaded_file.state.name}")

# Create model (no constraints, just basic)
print("\n[PROCESSING] Creating model and sending request...")
model = genai.GenerativeModel(model_name="gemini-2.5-flash")

# Simple prompt - just ask for the address
prompt = "What is the property address shown in this document?"

# Generate response
print(f"[PROCESSING] Sending prompt: '{prompt}'")
response = model.generate_content([uploaded_file, prompt])

# Print response
print("\n" + "=" * 80)
print("GEMINI RESPONSE:")
print("=" * 80)
print(response.text)
print("=" * 80)

# Clean up
genai.delete_file(uploaded_file.name)
print(f"\n[OK] Cleaned up file: {uploaded_file.name}")


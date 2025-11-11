"""Display the exact prompt being sent to Gemini."""

import os
import sys
from pathlib import Path

if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projectalphav1.settings")
    import django
    django.setup()

from etl.services.serv_etl_valuation_vision_extractor import PROMPT_TEMPLATE

print("=" * 80)
print("PROMPT BEING SENT TO GEMINI")
print("=" * 80)
print(f"Length: {len(PROMPT_TEMPLATE)} characters")
print(f"Estimated tokens: ~{len(PROMPT_TEMPLATE) // 4}")
print("=" * 80)
print()
print(PROMPT_TEMPLATE)
print()
print("=" * 80)
print("END OF PROMPT")
print("=" * 80)
print()
print("INSTRUCTIONS:")
print("1. Copy everything between the === lines above")
print("2. Go to https://aistudio.google.com/")
print("3. Upload the PDF: C:\\Users\\garre\\Documents\\2004954286.Pdf")
print("4. Paste this prompt")
print("5. Click 'Run' and see if it times out in the web interface too")



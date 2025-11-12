"""
Helper script to run ETL tests against TEST database instead of production.

Usage:
    python use_test_db.py <script_name> [args...]
    
Example:
    python use_test_db.py test_multipass.py "C:\Users\garre\Documents\2004954286.Pdf"
"""

import os
import sys
import subprocess

# Override DATABASE_URL to use test database
TEST_DATABASE_URL = 'postgresql://neondb_owner:npg_etXSFVQx7Nz3@ep-restless-term-afx5ynub-pooler.c-2.us-west-2.aws.neon.tech/neondb?channel_binding=require&sslmode=require'

if len(sys.argv) < 2:
    print("❌ Error: Please provide a script to run")
    print(f"Usage: {sys.argv[0]} <script_name> [args...]")
    sys.exit(1)

script_name = sys.argv[1]
script_args = sys.argv[2:]

print(f"🧪 Running {script_name} against TEST database...")
print(f"📍 Test branch: etl-testing (br-hidden-sound-af775rz8)")
print(f"⚠️  Production database will NOT be affected")
print("=" * 80)

# Set environment variable and run the script
env = os.environ.copy()
env['DATABASE_URL'] = TEST_DATABASE_URL

# Build command
cmd = [sys.executable, script_name] + script_args

# Run the script with modified environment
result = subprocess.run(cmd, env=env)

print("=" * 80)
if result.returncode == 0:
    print(f"✅ Test completed successfully!")
else:
    print(f"❌ Test failed with exit code {result.returncode}")

sys.exit(result.returncode)


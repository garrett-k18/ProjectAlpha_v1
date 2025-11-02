import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projectalphav1.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()
cursor.execute("""
    SELECT column_name, data_type, is_nullable 
    FROM information_schema.columns 
    WHERE table_name = 'square_footage_assumptions' 
    ORDER BY ordinal_position;
""")

print("\nColumns in square_footage_assumptions table:")
print("-" * 60)
for row in cursor.fetchall():
    print(f"{row[0]:40} {row[1]:20} NULL={row[2]}")
print("-" * 60)


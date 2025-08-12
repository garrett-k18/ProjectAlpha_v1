"""
Script to check database schemas and tables
"""
import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projectalphav1.settings')
django.setup()

# Now we can import Django models and use Django's database connections
from django.db import connections

def check_schemas():
    """Check tables in each schema"""
    print("Checking database schemas and tables...")
    
    # Check tables in default database (core schema)
    with connections['default'].cursor() as cursor:
        # List schemas
        cursor.execute("SELECT schema_name FROM information_schema.schemata;")
        schemas = cursor.fetchall()
        print("\nAvailable schemas:")
        for schema in schemas:
            print(f"- {schema[0]}")
        
        # List tables in core schema
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'core' AND table_type = 'BASE TABLE';")
        tables = cursor.fetchall()
        print("\nTables in 'core' schema:")
        for table in tables:
            print(f"- {table[0]}")
    
    # Check tables in seller_data database
    with connections['seller_data'].cursor() as cursor:
        # List tables in seller_data schema
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'seller_data' AND table_type = 'BASE TABLE';")
        tables = cursor.fetchall()
        print("\nTables in 'seller_data' schema:")
        for table in tables:
            print(f"- {table[0]}")

if __name__ == "__main__":
    check_schemas()

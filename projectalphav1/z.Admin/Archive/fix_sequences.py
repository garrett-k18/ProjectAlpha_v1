"""
Management command to fix PostgreSQL sequences for any table.

Usage:
    python manage.py fix_sequences                    # Fix all sequences
    python manage.py fix_sequences --table tablename  # Fix specific table
"""

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Fix PostgreSQL sequences that are out of sync with table data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--table',
            type=str,
            help='Specific table name to fix (omit to fix all sequences)',
        )

    def handle(self, *args, **options):
        table_name = options.get('table')
        
        with connection.cursor() as cursor:
            if table_name:
                # Fix specific table
                self.stdout.write(f"Fixing sequence for table: {table_name}")
                self.fix_table_sequence(cursor, table_name)
                return  # Exit after fixing specific table
            
            # Fix all sequences
            self.fix_all_sequences(cursor)

    def fix_table_sequence(self, cursor, table_name):
        """Fix sequence for a specific table."""
        try:
            # Get the primary key column name
            cursor.execute(f"""
                SELECT a.attname
                FROM pg_index i
                JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
                WHERE i.indrelid = '{table_name}'::regclass
                AND i.indisprimary;
            """)
            pk_result = cursor.fetchone()
            
            if not pk_result:
                self.stdout.write(self.style.WARNING(f"No primary key found for table: {table_name}"))
                return
            
            pk_column = pk_result[0]
            
            # Get the sequence name
            cursor.execute(f"""
                SELECT pg_get_serial_sequence('{table_name}', '{pk_column}');
            """)
            seq_result = cursor.fetchone()
            
            if not seq_result or not seq_result[0]:
                self.stdout.write(self.style.WARNING(f"No sequence found for {table_name}.{pk_column}"))
                return
            
            sequence_name = seq_result[0]
            
            # Get max ID from table
            cursor.execute(f"SELECT MAX({pk_column}) FROM {table_name};")
            max_id = cursor.fetchone()[0]
            
            if max_id is None:
                max_id = 0
            
            # Set sequence to max_id + 1
            next_id = max_id + 1
            cursor.execute(f"SELECT setval('{sequence_name}', %s, false);", [next_id])
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"SUCCESS: Fixed {table_name} sequence! Next ID will be: {next_id}"
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"ERROR: Failed to fix {table_name}: {str(e)}")
            )

    def fix_all_sequences(self, cursor):
        """Fix all sequences in the database."""
        self.stdout.write("Finding all tables with sequences...")
        
        # Get all tables with sequences
        cursor.execute("""
            SELECT 
                c.relname AS table_name,
                a.attname AS column_name,
                pg_get_serial_sequence(c.relname, a.attname) AS sequence_name
            FROM pg_class c
            JOIN pg_attribute a ON a.attrelid = c.oid
            WHERE c.relkind = 'r'
            AND a.attnum > 0
            AND NOT a.attisdropped
            AND pg_get_serial_sequence(c.relname, a.attname) IS NOT NULL
            ORDER BY c.relname;
        """)
        
        tables = cursor.fetchall()
        
        if not tables:
            self.stdout.write(self.style.WARNING("No sequences found"))
            return
        
        self.stdout.write(f"Found {len(tables)} table(s) with sequences\n")
        
        fixed_count = 0
        for table_name, column_name, sequence_name in tables:
            try:
                # Get max ID
                cursor.execute(f"SELECT MAX({column_name}) FROM {table_name};")
                max_id = cursor.fetchone()[0]
                
                if max_id is None:
                    max_id = 0
                
                # Get current sequence value
                cursor.execute(f"SELECT last_value FROM {sequence_name};")
                current_seq = cursor.fetchone()[0]
                
                next_id = max_id + 1
                
                # Only fix if out of sync
                if current_seq < next_id:
                    cursor.execute(f"SELECT setval('{sequence_name}', %s, false);", [next_id])
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"FIXED: {table_name}.{column_name}: {current_seq} -> {next_id}"
                        )
                    )
                    fixed_count += 1
                else:
                    self.stdout.write(
                        f"  {table_name}.{column_name}: OK (current: {current_seq}, next: {next_id})"
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"SKIP: {table_name}: {str(e)}")
                )
        
        self.stdout.write(
            self.style.SUCCESS(f"\nSUCCESS: Fixed {fixed_count} sequence(s)")
        )


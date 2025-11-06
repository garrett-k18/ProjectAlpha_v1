"""
Django management command to fix PostgreSQL sequence for MasterCRM table.

WHAT: Fixes auto-increment sequence when it's out of sync with actual data
WHY: Prevents "duplicate key value violates unique constraint" errors
HOW: Resets the sequence to MAX(id) from the table

Usage:
    python manage.py fix_mastercrm_sequence
"""

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Fix PostgreSQL sequence for core_mastercrm table'

    def handle(self, *args, **options):
        """
        WHAT: Reset the auto-increment sequence to match actual data
        WHY: Sequence can get out of sync after manual inserts or migrations
        HOW: Use setval() to set sequence to MAX(id) from table
        """
        with connection.cursor() as cursor:
            # WHAT: Reset sequence to the maximum ID in the table
            # WHY: Ensures next auto-generated ID won't conflict
            cursor.execute("""
                SELECT setval(
                    pg_get_serial_sequence('core_mastercrm', 'id'),
                    COALESCE((SELECT MAX(id) FROM core_mastercrm), 1),
                    true
                );
            """)
            
            result = cursor.fetchone()
            new_sequence_value = result[0] if result else None
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'SUCCESS: MasterCRM sequence fixed! Next ID will be: {new_sequence_value + 1}'
                )
            )


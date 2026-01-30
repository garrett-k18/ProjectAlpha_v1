"""
Management command to reset test environment (clear + generate).

This is a convenience command that combines clear_test_data and generate_test_data.

Usage:
    python manage.py reset_test_env --preset=minimal
    python manage.py reset_test_env --sellers=12 --assets-per-trade=20
    python manage.py reset_test_env --database=dev --no-input
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Clear all data and regenerate test environment'

    def add_arguments(self, parser):
        # Inherit arguments from generate_test_data
        parser.add_argument('--sellers', type=int, default=12)
        parser.add_argument('--trades-per-seller', type=str, default='1-2')
        parser.add_argument('--assets-per-trade', type=str, default='1-35')
        parser.add_argument('--preset', choices=['minimal', 'standard', 'full'])
        parser.add_argument('--database', type=str, default='default')
        parser.add_argument('--with-outcomes', action='store_true')
        parser.add_argument('--with-am-notes', action='store_true')
        parser.add_argument('--verbose', action='store_true')
        parser.add_argument('--no-input', action='store_true')

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.WARNING(
                '\n🔄 Resetting Test Environment\n'
                '=' * 50 + '\n'
            )
        )

        # Step 1: Clear data
        self.stdout.write('\n📋 Step 1: Clearing existing data...\n')
        call_command(
            'clear_test_data',
            no_input=options['no_input'],
            verbose=options['verbose']
        )

        # Step 2: Generate new data
        self.stdout.write('\n📋 Step 2: Generating new test data...\n')
        
        gen_options = {
            'sellers': options['sellers'],
            'trades_per_seller': options['trades_per_seller'],
            'assets_per_trade': options['assets_per_trade'],
            'database': options['database'],
            'with_outcomes': options['with_outcomes'],
            'with_am_notes': options['with_am_notes'],
            'verbose': options['verbose'],
        }
        
        if options.get('preset'):
            gen_options['preset'] = options['preset']
        
        call_command('generate_test_data', **gen_options)

        self.stdout.write(
            self.style.SUCCESS(
                '\n✅ Test environment reset complete!\n'
            )
        )

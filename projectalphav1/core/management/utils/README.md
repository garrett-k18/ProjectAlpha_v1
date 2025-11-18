# Production Database Import Utilities

## Overview

The `prod_db_helper.py` utility provides reusable functions for connecting to production databases in Django management commands. This eliminates the need to recreate complex database connection logic for every import command.

## Quick Start

### 1. Import the utilities

```python
from core.management.utils.prod_db_helper import add_prod_db_args, setup_prod_db, check_db_connection
```

### 2. Add arguments to your command

```python
def add_arguments(self, parser):
    # Your other arguments...
    parser.add_argument('--csv-file', type=str, default='data.csv')
    
    # Add production database flags (--prod, --database-url, --check-db)
    add_prod_db_args(parser)
```

### 3. Setup database connection in handle()

```python
def handle(self, *args, **options):
    # Check database connection (optional)
    if options.get('check_db'):
        check_db_connection(options, self)
        return
    
    # Setup production database if --prod flag is used
    db_alias = setup_prod_db(options, command_instance=self)
    
    # Use db_alias for all queries
    MyModel.objects.using(db_alias).all()
    MyModel.objects.using(db_alias).create(...)
```

## Example: Complete Command

```python
from django.core.management.base import BaseCommand
from core.management.utils.prod_db_helper import add_prod_db_args, setup_prod_db, check_db_connection
from core.models import MyModel

class Command(BaseCommand):
    help = 'Import data to production'
    
    def add_arguments(self, parser):
        parser.add_argument('--csv-file', type=str, default='data.csv')
        add_prod_db_args(parser)  # Adds --prod, --database-url, --check-db
    
    def handle(self, *args, **options):
        if options.get('check_db'):
            check_db_connection(options, self)
            return
        
        db_alias = setup_prod_db(options, command_instance=self)
        
        # Your import logic here
        records = MyModel.objects.using(db_alias).all()
        self.stdout.write(f'Found {records.count()} records')
```

## Usage

### Development (uses DATABASE_URL from .env)
```bash
python manage.py my_import_command --csv-file data.csv
```

### Production (uses proddb from .env)
```bash
python manage.py my_import_command --prod --csv-file data.csv
```

### Check database connection before running
```bash
python manage.py my_import_command --check-db
```

### Override with custom database URL
```bash
python manage.py my_import_command --database-url "postgresql://user:pass@host/db"
```

## Environment Variables

The utility checks for production database URL in this order:
1. `--database-url` command line argument
2. `PROD_DATABASE_URL` environment variable
3. `proddb` environment variable (legacy)
4. Hardcoded fallback (if none found)

## Features

- ✅ Handles Django 5.2+ database settings (CONN_HEALTH_CHECKS, TIME_ZONE)
- ✅ Preserves all existing database configuration
- ✅ Supports Neon database connection pooling
- ✅ Provides clear database connection feedback
- ✅ Easy to add to any management command


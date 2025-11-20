"""
WHAT: Reusable utility for connecting to production database in management commands
WHY: Avoid recreating complex database connection logic for every import command
HOW: Provides helper functions and argument parser additions for --prod flag

Usage in management commands:
    from core.management.utils.prod_db_helper import add_prod_db_args, setup_prod_db
    
    def add_arguments(self, parser):
        add_prod_db_args(parser)  # Adds --prod and --database-url flags
    
    def handle(self, *args, **options):
        db_alias = setup_prod_db(options)  # Returns 'default' with prod connection configured
        # Now use db_alias for all queries: Model.objects.using(db_alias).all()
"""

import os
from django.conf import settings
from django.db import connections
import dj_database_url


def add_prod_db_args(parser):
    """
    WHAT: Add database selection arguments to command parser
    WHY: Standardize database switching across all import commands
    HOW: Adds --prod, --database-url, and --check-db arguments
    
    Note: By default, commands use DB_ENVIRONMENT from .env (dev/newdev/prod/local)
    """
    parser.add_argument(
        '--prod',
        action='store_true',
        help='Force use of production database (DB_PROD from .env)',
    )
    parser.add_argument(
        '--database-url',
        dest='database_url',
        type=str,
        default=None,
        help='Override with a specific database connection string',
    )
    parser.add_argument(
        '--check-db',
        action='store_true',
        help='Show which database will be used and exit (does not run command)',
    )


def get_prod_db_url(options):
    """
    WHAT: Get database URL for import commands using IMPORT_DB system
    WHY: Separate import command database from Django app database
    HOW: Checks --database-url override, then --prod flag, then uses IMPORT_DB
    """
    database_url_override = options.get('database_url')
    use_prod = options.get('prod', False)
    
    # Priority 1: Explicit --database-url override
    if database_url_override:
        return database_url_override
    
    # Priority 2: --prod flag (uses DB_PROD)
    if use_prod:
        prod_db_url = os.getenv('DB_PROD')
        if prod_db_url:
            return prod_db_url
        # Fallback to legacy env vars
        prod_db_url = os.getenv('PROD_DATABASE_URL') or os.getenv('proddb')
        if prod_db_url:
            return prod_db_url
        # Final fallback to hardcoded production URL
        return "postgresql://neondb_owner:npg_etXSFVQx7Nz3@ep-sweet-unit-afg5w70r.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    
    # Priority 3: Use IMPORT_DB setting (separate from Django app database)
    # This allows you to view dev data while importing to prod
    import_db = os.getenv('IMPORT_DB', '').lower()
    if import_db:
        env_map = {
            'dev': os.getenv('DB_DEV'),
            'newdev': os.getenv('DB_NEWDEV'),
            'prod': os.getenv('DB_PROD'),
        }
        import_url = env_map.get(import_db)
        if import_url:
            return import_url
    
    # Priority 4: Fall back to Django's DATABASE_URL
    return None  # Will use default DATABASE_URL from settings


def setup_prod_db(options, command_instance=None):
    """
    WHAT: Configure database connection for production if --prod flag is used
    WHY: Handle all the complex Django database connection setup in one place
    HOW: Copies existing config, updates connection details, ensures all Django 5.2+ fields exist
    
    Args:
        options: Command options dict (from add_arguments)
        command_instance: Optional command instance for output messages
    
    Returns:
        str: Database alias to use ('default' with production connection configured)
    """
    database_url_override = get_prod_db_url(options)
    
    if not database_url_override:
        # No override, use default database from .env
        return options.get('database', 'default')
    
    # WHAT: Parse production database URL
    # WHY: Need to extract connection details
    db_config = dj_database_url.parse(
        database_url_override,
        conn_max_age=600,
        ssl_require=True,
    )
    
    # WHAT: Check if this is a Neon database
    # WHY: Neon requires special handling (unpooled connection)
    is_neon = 'neon.tech' in db_config.get('HOST', '')
    if is_neon:
        db_config['HOST'] = db_config['HOST'].replace('-pooler', '')
    
    # WHAT: Copy existing default config completely, then override connection details
    # WHY: Preserve ALL Django database settings (TIME_ZONE, CONN_HEALTH_CHECKS, etc.)
    # HOW: Deep copy to avoid modifying original, then update only connection fields
    import copy
    existing_default = copy.deepcopy(settings.DATABASES.get('default', {}))
    
    # WHAT: Update only the connection fields, keep everything else
    # WHY: Preserve all Django internal settings that might be needed
    # HOW: Use update() to override connection details while preserving other fields
    existing_default.update({
        'ENGINE': db_config.get('ENGINE', 'django.db.backends.postgresql'),
        'NAME': db_config.get('NAME'),
        'USER': db_config.get('USER'),
        'PASSWORD': db_config.get('PASSWORD'),
        'HOST': db_config.get('HOST'),
        'PORT': db_config.get('PORT'),
        'CONN_MAX_AGE': db_config.get('CONN_MAX_AGE', 600),
        'OPTIONS': {
            'options': '-c search_path=core,seller_data,public'
        },
    })
    
    # WHAT: Ensure Django 5.2+ required fields exist with proper defaults
    # WHY: Django 5.2+ expects these fields in settings_dict to avoid KeyError
    # HOW: Check each field and set if missing, using safe defaults
    
    # WHAT: CONN_HEALTH_CHECKS - Django 5.1+ field for connection health monitoring
    # WHY: Required to avoid KeyError when Django accesses this field
    # HOW: Default to False (disabled) if not present
    if 'CONN_HEALTH_CHECKS' not in existing_default:
        existing_default['CONN_HEALTH_CHECKS'] = False
    
    # WHAT: TIME_ZONE - Optional database-level timezone override
    # WHY: Some Django versions may access this field, should match settings.TIME_ZONE
    # HOW: Get from settings with safe fallback to 'UTC' if not set
    if 'TIME_ZONE' not in existing_default:
        # WHAT: Get TIME_ZONE from settings with safe fallback
        # WHY: settings.TIME_ZONE might not exist in older Django versions
        # HOW: Use getattr with 'UTC' as default fallback
        time_zone = getattr(settings, 'TIME_ZONE', 'UTC')
        existing_default['TIME_ZONE'] = time_zone
    
    # WHAT: Ensure ATOMIC_REQUESTS is preserved if it exists
    # WHY: Django database setting for transaction management
    # HOW: Preserve existing value if present (already handled by deepcopy, but explicit for clarity)
    if 'ATOMIC_REQUESTS' not in existing_default:
        # WHAT: Default to False if not set
        # WHY: Not all apps need atomic requests per view
        # HOW: Set explicitly to avoid any potential issues
        existing_default['ATOMIC_REQUESTS'] = False
    
    # WHAT: Ensure AUTOCOMMIT is preserved if it exists
    # WHY: Django database setting for transaction control
    # HOW: Preserve existing value (handled by deepcopy) or set default
    if 'AUTOCOMMIT' not in existing_default:
        # WHAT: Default to True (Django default)
        # WHY: Standard Django behavior
        # HOW: Set explicitly to ensure consistency
        existing_default['AUTOCOMMIT'] = True
    
    # WHAT: Update both settings and connections databases
    # WHY: Ensure Django uses the new config with all fields preserved
    settings.DATABASES['default'] = existing_default
    
    # WHAT: Close existing connection and update connections registry
    # WHY: Ensure we connect to the new database, not cached connections
    if 'default' in connections.databases:
        connections.databases['default'] = existing_default
    if hasattr(connections['default'], 'close'):
        connections['default'].close()
    # WHAT: Force re-initialization of connection with new settings
    # WHY: Connection needs to use new config when accessed next
    connections['default'].settings_dict = existing_default
    
    # WHAT: Output confirmation message if command instance provided
    # WHY: Let user know which database is being used for imports
    if command_instance:
        host = db_config.get('HOST', 'unknown')
        if 'ep-sweet-unit' in host:
            command_instance.stdout.write(command_instance.style.SUCCESS('📥 Import Target: PRODUCTION database'))
        elif 'ep-icy-haze' in host:
            command_instance.stdout.write(command_instance.style.WARNING('📥 Import Target: DEVELOPMENT database'))
        elif 'ep-orange-hat' in host:
            command_instance.stdout.write(command_instance.style.WARNING('📥 Import Target: NEWDEV database'))
        command_instance.stdout.write(f'Database: {db_config.get("NAME", "unknown")} | Host: {host}')
    
    return 'default'


def check_db_connection(options, command_instance):
    """
    WHAT: Show which database will be used without actually running the command
    WHY: Allow verification before running imports
    HOW: Parses database URL and shows connection details
    """
    database_url_override = get_prod_db_url(options)
    
    command_instance.stdout.write(command_instance.style.WARNING('\n=== DATABASE CONNECTION CHECK ==='))
    
    if database_url_override:
        command_instance.stdout.write(command_instance.style.WARNING('Using override database URL'))
        # Parse to show details
        db_config = dj_database_url.parse(database_url_override, conn_max_age=600, ssl_require=True)
        is_neon = 'neon.tech' in db_config.get('HOST', '')
        if is_neon:
            db_config['HOST'] = db_config['HOST'].replace('-pooler', '')
        
        command_instance.stdout.write(f'  Host: {db_config.get("HOST", "unknown")}')
        command_instance.stdout.write(f'  Database: {db_config.get("NAME", "unknown")}')
        command_instance.stdout.write(f'  User: {db_config.get("USER", "unknown")}')
        
        if 'ep-sweet-unit' in db_config.get('HOST', ''):
            command_instance.stdout.write(command_instance.style.SUCCESS('  ✓ PRODUCTION DATABASE'))
        elif 'ep-icy-haze' in db_config.get('HOST', ''):
            command_instance.stdout.write(command_instance.style.WARNING('  ⚠ DEVELOPMENT DATABASE'))
        else:
            command_instance.stdout.write(command_instance.style.WARNING('  ⚠ UNKNOWN DATABASE'))
    else:
        # Show default database from .env
        db_alias = options.get('database', 'default')
        db_config = settings.DATABASES.get(db_alias, {})
        command_instance.stdout.write(f'Using default database from DATABASE_URL (.env)')
        command_instance.stdout.write(f'  Host: {db_config.get("HOST", "unknown")}')
        command_instance.stdout.write(f'  Database: {db_config.get("NAME", "unknown")}')
        command_instance.stdout.write(f'  User: {db_config.get("USER", "unknown")}')
        
        if 'ep-sweet-unit' in db_config.get('HOST', ''):
            command_instance.stdout.write(command_instance.style.SUCCESS('  ✓ PRODUCTION DATABASE'))
        elif 'ep-icy-haze' in db_config.get('HOST', ''):
            command_instance.stdout.write(command_instance.style.WARNING('  ⚠ DEVELOPMENT DATABASE'))
        else:
            command_instance.stdout.write(command_instance.style.WARNING('  ⚠ UNKNOWN DATABASE'))
    
    command_instance.stdout.write(command_instance.style.WARNING('===================================\n'))


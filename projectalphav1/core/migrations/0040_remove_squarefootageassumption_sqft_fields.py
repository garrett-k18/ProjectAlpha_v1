# Generated manually to remove sqft_min and sqft_max fields
# These fields were part of the original design but have been refactored out
# The model now uses per-square-foot costs that are multiplied by actual property square footage
# Using RunSQL because these columns exist in the database but were never tracked in Django migrations

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0039_alter_hoaassumption_property_type_and_more'),
    ]

    operations = [
        # Use raw SQL to drop columns that exist in database but not in migration history
        migrations.RunSQL(
            # Forward SQL - drop the columns
            sql="""
                ALTER TABLE square_footage_assumptions 
                DROP COLUMN IF EXISTS sqft_min;
                
                ALTER TABLE square_footage_assumptions 
                DROP COLUMN IF EXISTS sqft_max;
            """,
            # Reverse SQL - add them back if we need to rollback (nullable to avoid data issues)
            reverse_sql="""
                ALTER TABLE square_footage_assumptions 
                ADD COLUMN IF NOT EXISTS sqft_min INTEGER NULL;
                
                ALTER TABLE square_footage_assumptions 
                ADD COLUMN IF NOT EXISTS sqft_max INTEGER NULL;
            """,
        ),
    ]


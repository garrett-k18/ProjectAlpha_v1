from django.db import migrations

class Migration(migrations.Migration):
    initial = True

    # No dependencies; this must run before any CreateModel migrations to ensure schemas exist.
    dependencies = []

    operations = [
        migrations.RunSQL("CREATE SCHEMA IF NOT EXISTS core;"),
        migrations.RunSQL("CREATE SCHEMA IF NOT EXISTS seller_data;"),
    ]

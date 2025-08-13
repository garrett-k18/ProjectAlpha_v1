# Move seller models to seller_data schema

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('acq_module', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            # SQL to move tables from core to seller_data schema
            """
            -- Move seller models to seller_data schema
            ALTER TABLE IF EXISTS core.acq_module_seller SET SCHEMA seller_data;
            ALTER TABLE IF EXISTS core.acq_module_trade SET SCHEMA seller_data;
            ALTER TABLE IF EXISTS core.acq_module_sellerrawdata SET SCHEMA seller_data;
            """,
            # Reverse SQL to move back if needed
            """
            -- Move seller models back to core schema
            ALTER TABLE IF EXISTS seller_data.acq_module_seller SET SCHEMA core;
            ALTER TABLE IF EXISTS seller_data.acq_module_trade SET SCHEMA core;
            ALTER TABLE IF EXISTS seller_data.acq_module_sellerrawdata SET SCHEMA core;
            """
        ),
    ]
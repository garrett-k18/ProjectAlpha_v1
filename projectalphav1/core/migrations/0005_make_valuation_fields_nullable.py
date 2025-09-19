from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_add_bv_created_updated_by'),
    ]

    operations = [
        # Make InternalValuation fields nullable
        migrations.AlterField(
            model_name='internalvaluation',
            name='internal_asis_value',
            field=models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='internalvaluation',
            name='internal_arv_value',
            field=models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='internalvaluation',
            name='internal_value_date',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='internalvaluation',
            name='thirdparty_asis_value',
            field=models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='internalvaluation',
            name='thirdparty_arv_value',
            field=models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='internalvaluation',
            name='thirdparty_value_date',
            field=models.DateField(null=True, blank=True),
        ),
        
        # BrokerValues fields are already nullable, but let's ensure all are
        migrations.AlterField(
            model_name='brokervalues',
            name='broker_asis_value',
            field=models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='brokervalues',
            name='broker_arv_value',
            field=models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='brokervalues',
            name='broker_value_date',
            field=models.DateField(null=True, blank=True),
        ),
    ]

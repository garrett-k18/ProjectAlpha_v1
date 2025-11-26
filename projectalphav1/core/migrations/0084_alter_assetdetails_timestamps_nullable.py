# Generated migration to allow NULL timestamps on AssetDetails
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0083_alter_assetidhub_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assetdetails',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='assetdetails',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True, blank=True),
        ),
    ]

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Adds CustomAssetList model to support AM custom lists.
    """

    dependencies = [
        ('core', '0101_assetdetails_asset_class'),
        ('am_module', '0078_alter_delinquenttask_task_type'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomAssetList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='am_custom_lists', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Custom Asset List',
                'verbose_name_plural': 'Custom Asset Lists',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddField(
            model_name='customassetlist',
            name='assets',
            field=models.ManyToManyField(blank=True, related_name='am_custom_lists', to='core.assetidhub'),
        ),
    ]

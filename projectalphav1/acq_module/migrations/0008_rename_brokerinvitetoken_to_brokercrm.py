# Generated manually to rename BrokerInviteToken to Brokercrm and add new fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("acq_module", "0007_alter_brokerphoto_photo_brokerinvitetoken"),
    ]

    operations = [
        # Preserve existing table `acq_broker_invite_token` and data
        migrations.RenameModel(
            old_name="BrokerInviteToken",
            new_name="Brokercrm",
        ),
        # Add new optional metadata fields added in the new model
        migrations.AddField(
            model_name="brokercrm",
            name="broker_firm",
            field=models.CharField(max_length=255, blank=True, null=True),
        ),
        migrations.AddField(
            model_name="brokercrm",
            name="broker_state",
            field=models.CharField(max_length=2, blank=True, null=True),
        ),
        migrations.AddField(
            model_name="brokercrm",
            name="broker_msa",
            field=models.CharField(max_length=255, blank=True, null=True),
        ),
    ]

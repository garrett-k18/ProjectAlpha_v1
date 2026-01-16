# Generated migration for adding must_change_password field to UserProfile
# This field tracks if a user needs to change their temporary password on first login

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_admin', '0003_userassetaccess'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='must_change_password',
            field=models.BooleanField(default=False, help_text='Flag to indicate if user must change their password on next login. Set to True when admin creates user with temporary password.'),
        ),
    ]

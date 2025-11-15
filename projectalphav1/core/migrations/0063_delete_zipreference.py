from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0062_hudzipcbsacrosswalk'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ZIPReference',
        ),
    ]


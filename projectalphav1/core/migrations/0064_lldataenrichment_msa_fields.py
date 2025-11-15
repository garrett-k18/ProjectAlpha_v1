from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0063_delete_zipreference"),
    ]

    operations = [
        migrations.AddField(
            model_name="lldataenrichment",
            name="geocode_msa_code",
            field=models.CharField(
                blank=True,
                help_text="MSA/CBSA code returned by Geocodio census append.",
                max_length=10,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="lldataenrichment",
            name="geocode_msa",
            field=models.CharField(
                blank=True,
                help_text="Human-friendly MSA name returned by Geocodio census append.",
                max_length=255,
                null=True,
            ),
        ),
    ]




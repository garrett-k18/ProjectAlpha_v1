from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0096_calendarevent_assigned_to_calendarevent_priority_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="calendarevent",
            name="completed",
            field=models.BooleanField(
                default=False,
                help_text="Has the task/event been completed?",
            ),
        ),
        migrations.AddIndex(
            model_name="calendarevent",
            index=models.Index(
                fields=["completed", "date"],
                name="core_calend_completed_date_idx",
            ),
        ),
    ]

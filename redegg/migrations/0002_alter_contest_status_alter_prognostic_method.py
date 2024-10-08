# Generated by Django 4.2.6 on 2023-11-20 15:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("redegg", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contest",
            name="status",
            field=models.CharField(
                choices=[("open", "Open"), ("live", "Live"), ("closed", "Closed")],
                default="open",
                max_length=10,
            ),
        ),
        migrations.AlterField(
            model_name="prognostic",
            name="method",
            field=models.CharField(
                blank=True,
                choices=[
                    ("decision", "Decision"),
                    ("ko_tko", "KO/TKO"),
                    ("submission", "Submission"),
                    ("cnc", "CNC (Could not continue)"),
                ],
                max_length=10,
                null=True,
            ),
        ),
    ]

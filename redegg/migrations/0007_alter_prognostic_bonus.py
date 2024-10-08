# Generated by Django 4.2.6 on 2023-11-25 11:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("redegg", "0006_prediction_prediction_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="prognostic",
            name="bonus",
            field=models.CharField(
                blank=True,
                choices=[
                    ("fight", "Fight of the Night"),
                    ("perf", "Performance of the Night"),
                    ("ko", "KO of the Night"),
                    ("sub", "Submission of the Night"),
                ],
                max_length=20,
                null=True,
            ),
        ),
    ]

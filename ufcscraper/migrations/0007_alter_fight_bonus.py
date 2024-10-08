# Generated by Django 4.2.6 on 2023-11-20 15:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ufcscraper", "0006_fight_position"),
    ]

    operations = [
        migrations.AlterField(
            model_name="fight",
            name="bonus",
            field=models.CharField(
                blank=True,
                choices=[
                    ("fight", "Fight of the Night"),
                    ("perf", "Performance of the Night"),
                    ("ko", "Knockout of the Night"),
                    ("submission", "Submission of the Night"),
                ],
                max_length=20,
                null=True,
            ),
        ),
    ]

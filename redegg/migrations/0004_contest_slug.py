# Generated by Django 4.2.6 on 2023-11-23 15:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("redegg", "0003_prognostic_bonus_percentage_prognostic_bonus_won_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="contest",
            name="slug",
            field=models.SlugField(blank=True, unique=True),
        ),
    ]

# Generated by Django 4.2.6 on 2023-11-23 13:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("redegg", "0002_alter_contest_status_alter_prognostic_method"),
    ]

    operations = [
        migrations.AddField(
            model_name="prognostic",
            name="bonus_percentage",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="prognostic",
            name="bonus_won",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="prognostic",
            name="fight_result_won",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="prognostic",
            name="method_won",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="prognostic",
            name="points",
            field=models.IntegerField(default=0),
        ),
    ]

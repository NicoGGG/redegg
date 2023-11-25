# Generated by Django 4.2.6 on 2023-11-25 11:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ufcscraper", "0009_alter_fight_bonus_alter_fight_weight_class"),
    ]

    operations = [
        migrations.AlterField(
            model_name="fight",
            name="method",
            field=models.CharField(
                blank=True,
                choices=[
                    ("U-DEC", "Unanimous Decision"),
                    ("S-DEC", "Split Decision"),
                    ("M-DEC", "Majority Decision"),
                    ("KO/TKO", "Knockout/Technical Knockout"),
                    ("SUB", "Submission"),
                    ("CNC", "Could Not Continue"),
                    ("Overturned", "Overturned"),
                    ("DQ", "Disqualification"),
                ],
                max_length=20,
                null=True,
            ),
        ),
    ]

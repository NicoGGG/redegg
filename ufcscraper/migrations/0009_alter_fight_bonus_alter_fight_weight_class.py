# Generated by Django 4.2.6 on 2023-11-23 15:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ufcscraper", "0008_fight_winner"),
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
                    ("sub", "Submission of the Night"),
                ],
                max_length=20,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="fight",
            name="weight_class",
            field=models.CharField(
                choices=[
                    ("Super Heavyweight", "Super Heavyweight"),
                    ("Heavyweight", "Heavyweight"),
                    ("Light Heavyweight", "Light Heavyweight"),
                    ("Middleweight", "Middleweight"),
                    ("Welterweight", "Welterweight"),
                    ("Lightweight", "Lightweight"),
                    ("Featherweight", "Featherweight"),
                    ("Bantamweight", "Bantamweight"),
                    ("Flyweight", "Flyweight"),
                    ("Women's Featherweight", "Women's Featherweight"),
                    ("Women's Bantamweight", "Women's Bantamweight"),
                    ("Women's Flyweight", "Women's Flyweight"),
                    ("Women's Strawweight", "Women's Strawweight"),
                    ("Catch Weight", "Catch Weight"),
                    ("Open Weight", "Open Weight"),
                ],
                max_length=50,
            ),
        ),
    ]

# Generated by Django 4.2.6 on 2023-11-14 15:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.contrib.auth.models import User
import os


def create_superuser(apps, schema_editor):
    User.objects.create_superuser(
        "admin", "redegg@pm.me", os.environ.get("ADMIN_PASSWORD", "admin01")
    )


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("ufcscraper", "0006_fight_position"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Contest",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("open", "Open"),
                            ("live", "Live"),
                            ("finished", "Finished"),
                        ],
                        default="open",
                        max_length=10,
                    ),
                ),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="ufcscraper.event",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Prediction",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("score", models.IntegerField(default=0)),
                (
                    "contest",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="redegg.contest"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {("user", "contest")},
            },
        ),
        migrations.CreateModel(
            name="Prognostic",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("is_draw", models.BooleanField(default=False)),
                (
                    "method",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("decision", "Decision"),
                            ("ko_tko", "KO/TKO"),
                            ("submission", "Submission"),
                            ("cnc", "CNC"),
                        ],
                        max_length=10,
                        null=True,
                    ),
                ),
                (
                    "bonus",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("fight", "Fight of the Night"),
                            ("perf", "Performance of the Night"),
                            ("ko", "KO of the Night"),
                            ("submission", "Submission of the Night"),
                        ],
                        max_length=20,
                        null=True,
                    ),
                ),
                (
                    "fight",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="ufcscraper.fight",
                    ),
                ),
                (
                    "fight_result",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="ufcscraper.fighter",
                    ),
                ),
                (
                    "prediction",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="redegg.prediction",
                    ),
                ),
            ],
        ),
        migrations.RunPython(create_superuser),
    ]

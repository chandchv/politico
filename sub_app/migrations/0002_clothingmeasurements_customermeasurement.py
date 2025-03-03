# Generated by Django 5.1.3 on 2025-03-02 09:04

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sub_app", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ClothingMeasurements",
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
                    "clothing_type",
                    models.CharField(
                        choices=[
                            ("shirt", "Shirt"),
                            ("pants", "Pants"),
                            ("suit", "Suit"),
                            ("kurta", "Kurta"),
                            ("blazer", "Blazer"),
                            ("sherwani", "Sherwani"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "measurement_fields",
                    models.JSONField(
                        default=dict,
                        help_text="Dictionary of required measurements for this clothing type",
                    ),
                ),
                ("description", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "unique_together": {("clothing_type",)},
            },
        ),
        migrations.CreateModel(
            name="CustomerMeasurement",
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
                ("measurements", models.JSONField(default=dict)),
                ("notes", models.TextField(blank=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "clothing_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="sub_app.clothingmeasurements",
                    ),
                ),
                (
                    "measured_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="measurements_taken",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="customer_measurements",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {("user", "clothing_type")},
            },
        ),
    ]

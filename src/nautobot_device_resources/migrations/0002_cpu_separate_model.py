# pylint: disable=invalid-name
# Generated by Django 3.2.16 on 2023-02-20 11:41

import uuid

import django.core.serializers.json
import django.db.models.deletion
import nautobot.core.fields
import nautobot.extras.models.mixins
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    dependencies = [
        ("dcim", "0019_device_redundancy_group_data_migration"),
        ("nautobot_device_resources", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="deviceresource",
            name="cpu_cores",
        ),
        migrations.AddField(
            model_name="deviceresource",
            name="cpu_count",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="deviceresource",
            name="ram",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name="CPU",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("created", models.DateField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "_custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
                ),
                ("name", models.CharField(max_length=200)),
                (
                    "slug",
                    nautobot.core.fields.AutoSlugField(blank=True, max_length=100, populate_from="name", unique=True),
                ),
                ("cores", models.PositiveSmallIntegerField()),
                ("threads_per_core", models.PositiveSmallIntegerField(default=2)),
                (
                    "manufacturer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, related_name="cpus", to="dcim.manufacturer"
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
                "verbose_name": "CPU",
                "verbose_name_plural": "CPUs",
            },
            bases=(
                models.Model,
                nautobot.extras.models.mixins.DynamicGroupMixin,
                nautobot.extras.models.mixins.NotesMixin,
            ),
        ),
        migrations.AlterField(
            model_name="deviceresource",
            name="cpu",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="instances",
                to="nautobot_device_resources.cpu",
            ),
        ),
    ]
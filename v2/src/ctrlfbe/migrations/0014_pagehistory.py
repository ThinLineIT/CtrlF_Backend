# Generated by Django 3.2.4 on 2021-12-16 07:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ctrlf_auth", "0003_auto_20210808_0110"),
        ("ctrlfbe", "0013_remove_page_summary"),
    ]

    operations = [
        migrations.CreateModel(
            name="PageHistory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=100)),
                ("content", models.TextField()),
                ("is_approved", models.BooleanField(default=False)),
                (
                    "version_type",
                    models.CharField(choices=[("LATEST", "최신"), ("UPDATE", "수정요청"), ("PAST", "과거")], max_length=30),
                ),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="ctrlf_auth.ctrlfuser")),
                ("page", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="ctrlfbe.page")),
            ],
            options={
                "abstract": False,
            },
        ),
    ]

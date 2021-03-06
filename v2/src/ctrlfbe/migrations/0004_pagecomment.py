# Generated by Django 3.2.5 on 2021-08-08 04:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ctrlf_auth", "0003_auto_20210808_0110"),
        ("ctrlfbe", "0003_auto_20210808_0420"),
    ]

    operations = [
        migrations.CreateModel(
            name="PageComment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=100)),
                ("content", models.TextField()),
                ("page", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="ctrlfbe.page")),
                (
                    "user",
                    models.ForeignKey(
                        help_text="페이지의 코멘트를 생성한 유저",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="ctrlf_auth.ctrlfuser",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]

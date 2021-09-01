# Generated by Django 3.2.5 on 2021-09-01 06:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ctrlfbe", "0005_page_is_approved"),
    ]

    operations = [
        migrations.AddField(
            model_name="contentrequest",
            name="status",
            field=models.CharField(
                choices=[("PENDING", "보류"), ("REJECTED", "거절"), ("ACCEPTED", "승인")],
                default="PENDING",
                help_text="Content 상태들",
                max_length=30,
            ),
        ),
        migrations.AlterField(
            model_name="issue",
            name="status",
            field=models.CharField(
                choices=[("REQUESTED", "요청"), ("CLOSED", "닫힘")], help_text="Issue 상태들", max_length=30
            ),
        ),
    ]

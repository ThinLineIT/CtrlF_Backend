# Generated by Django 3.2.4 on 2021-11-06 05:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ctrlfbe", "0008_auto_20211106_1359"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="issue",
            name="content",
        ),
        migrations.AddField(
            model_name="issue",
            name="reason",
            field=models.TextField(default="", help_text="NOTE, TOPIC, PAGE CRUD에 대한 설명"),
        ),
    ]

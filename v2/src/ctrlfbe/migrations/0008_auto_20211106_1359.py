# Generated by Django 3.2.4 on 2021-11-06 04:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("ctrlfbe", "0007_delete_pagecomment"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="issue",
            name="content_request",
        ),
        migrations.DeleteModel(
            name="ContentRequest",
        ),
    ]

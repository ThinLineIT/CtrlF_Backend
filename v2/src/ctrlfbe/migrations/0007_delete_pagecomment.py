# Generated by Django 3.2.4 on 2021-11-06 04:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("ctrlfbe", "0006_page_summary"),
    ]

    operations = [
        migrations.DeleteModel(
            name="PageComment",
        ),
    ]

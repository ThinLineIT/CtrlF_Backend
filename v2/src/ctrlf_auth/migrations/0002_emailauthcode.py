# Generated by Django 3.2.5 on 2021-07-24 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ctrlf_auth", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="EmailAuthCode",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(help_text="이메일 인증용 코드", max_length=8)),
            ],
        ),
    ]

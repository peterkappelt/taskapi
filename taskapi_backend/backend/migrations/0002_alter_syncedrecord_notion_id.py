# Generated by Django 4.2.1 on 2023-10-09 13:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("backend", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="syncedrecord",
            name="notion_id",
            field=models.CharField(max_length=36, null=True),
        ),
    ]

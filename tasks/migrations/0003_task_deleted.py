# Generated by Django 4.2.5 on 2023-09-20 14:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tasks", "0002_task_created_date"),
    ]

    operations = [
        migrations.AddField(
            model_name="task",
            name="deleted",
            field=models.BooleanField(default=False),
        ),
    ]

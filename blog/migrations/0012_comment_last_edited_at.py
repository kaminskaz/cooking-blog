# Generated by Django 5.1.4 on 2025-01-02 21:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0011_remove_recipe_instructions_recipe_instructions"),
    ]

    operations = [
        migrations.AddField(
            model_name="comment",
            name="last_edited_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]

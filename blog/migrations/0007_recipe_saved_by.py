# Generated by Django 5.1.4 on 2024-12-30 21:05

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0006_remove_recipe_saved_by"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="recipe",
            name="saved_by",
            field=models.ManyToManyField(
                blank=True, related_name="saved_recipes", to=settings.AUTH_USER_MODEL
            ),
        ),
    ]

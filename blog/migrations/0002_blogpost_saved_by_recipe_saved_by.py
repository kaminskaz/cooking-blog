# Generated by Django 5.1.4 on 2024-12-30 18:15

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="blogpost",
            name="saved_by",
            field=models.ManyToManyField(
                blank=True, related_name="saved_posts", to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="recipe",
            name="saved_by",
            field=models.ManyToManyField(
                blank=True, related_name="saved_recipes", to=settings.AUTH_USER_MODEL
            ),
        ),
    ]

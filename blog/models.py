

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# models.py
from django.db import models
from django.utils import timezone


class Ingredient(models.Model):
    UNIT_CHOICES = [
        ('g', 'grams'),
        ('kg', 'kilograms'),
        ('ml', 'milliliters'),
        ('l', 'liters'),
        ('tsp', 'teaspoon'),
        ('tbsp', 'tablespoon'),
        ('cup', 'cup'),
        ('oz', 'ounces'),
        ('lb', 'pounds'),
        # Add more units as needed
    ]
    ALLERGEN_CHOICES = [
        ('gluten', 'Gluten'),
        ('dairy', 'Dairy'),
        ('eggs', 'Eggs'),
        ('nuts', 'Nuts'),
        ('soy', 'Soy'),
        ('seafood', 'Seafood'),
    ]

    name = models.CharField(max_length=100)
    number = models.FloatField()
    units = models.CharField(max_length=50, choices=UNIT_CHOICES, null=True, blank=True)
    contains_allergen = models.CharField(max_length=50, choices=ALLERGEN_CHOICES, null=True, blank=True)

    def __str__(self):
        number_display = int(self.number) if self.number.is_integer() else self.number
        units_display = f" {self.units}" if self.units else ""
        return f"{number_display}{units_display} of {self.name}"

class Recipe(models.Model):
    FOOD_NAME_CHOICES = [
        ('pasta', 'Pasta'),
        ('salad', 'Salad'),
        ('soup', 'Soup'),
        ('sandwich', 'Sandwich'),
        ('burger', 'Burger'),
        ('pizza', 'Pizza'),
        ('wrap', 'Wrap'),
        ('sauce', 'Sauce'),
        ('dessert', 'Dessert'),
        ('cake', 'Cake'),
        ('cookie', 'Cookie'),
        ('drink', 'Drink'),
        ('other', 'Other'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    ingredients = models.ManyToManyField('Ingredient')
    instructions = models.ManyToManyField('Instruction', related_name='recipe_instructions', blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    saved_by = models.ManyToManyField(User, related_name='saved_recipes', blank=True)
    average_rating = models.FloatField(default=0)
    image = models.ImageField(upload_to='recipe_images/', null=True, blank=True)
    food_category = models.CharField(max_length=100, choices=FOOD_NAME_CHOICES, null=True, blank=True)

    def __str__(self):
        return self.title

    def calculate_average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            average = sum(rating.rating for rating in ratings) / ratings.count()
            self.average_rating = average
            self.save()
        else:
            self.average_rating = 0
            self.save()

class Instruction(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='instruction_steps')
    step_number = models.IntegerField()
    text = models.TextField()
    image = models.ImageField(upload_to='instruction_images/', null=True, blank=True)  # New field

    class Meta:
        ordering = ['step_number']

    def __str__(self):
        return f"Step {self.step_number} for {self.recipe.title}"


class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='blog_images/', null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    saved_by = models.ManyToManyField(User, related_name='saved_posts', blank=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return self.title

class Comment(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, null=True, blank=True)
    blog_post = models.ForeignKey(BlogPost, related_name='comments', on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    last_edited_at = models.DateTimeField(null=True, blank=True)

    def clean(self):
        super().clean()
        self.validate_content()

    def validate_content(self):
        if not self.content:
            raise ValidationError('Comment content cannot be empty.')
        if len(self.content) > 500:
            raise ValidationError('Comment content cannot exceed 500 characters.')

    def save(self, *args, **kwargs):
        if self.pk:
            self.last_edited_at = timezone.now()
        self.full_clean()  # Ensure the clean method is called before saving
        super().save(*args, **kwargs)

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE, related_name='ratings')
    rating = models.FloatField()

    class Meta:
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f"{self.user.username} - {self.recipe.title} - {self.rating}"


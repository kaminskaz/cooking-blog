from django.contrib import admin
from .forms import RecipeAdminForm
from .models import Recipe, BlogPost, Comment, Instruction, Ingredient

admin.site.register(BlogPost)
admin.site.register(Comment)

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    form = RecipeAdminForm
    list_display = ('title', 'author', 'created_at', 'food_category')
    search_fields = ('title', 'description')
    list_filter = ('created_at', 'author','food_category')

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Instruction)
class InstructionAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'step_number')
    search_fields = ('text',)
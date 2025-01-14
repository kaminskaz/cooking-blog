from django.contrib.auth import login
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from .forms import CommentForm, RecipeRatingForm, RegistrationForm
from .models import Recipe, BlogPost, Comment, Rating

from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def blog_list(request):
    blog_posts = BlogPost.objects.all().order_by('-created_at')
    return render(request, 'blog/blog_list.html', {'blog_posts': blog_posts})

def recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    instructions = recipe.instruction_steps.all()
    comments = Comment.objects.filter(recipe=recipe)
    rating_form = RecipeRatingForm()
    comment_form = CommentForm()
    allergens = recipe.ingredients.filter(contains_allergen__isnull=False).values_list('contains_allergen', flat=True).distinct()

    if request.method == "POST":
        if 'rating' in request.POST:
            rating_form = RecipeRatingForm(request.POST)
            if rating_form.is_valid():
                rating, created = Rating.objects.update_or_create(
                    user=request.user,
                    recipe=recipe,
                    defaults={'rating': rating_form.cleaned_data['rating']}
                )
                recipe.calculate_average_rating()
                return redirect('recipe_detail', pk=pk)
        else:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.recipe = recipe
                comment.author = request.user
                comment.save()
                return redirect('recipe_detail', pk=pk)

    return render(request, 'blog/recipe_detail.html', {
        'recipe': recipe,
        'instructions': instructions,
        'comments': comments,
        'rating_form': rating_form,
        'comment_form': comment_form,
        'allergens': allergens
    })

def recipe_list(request):
    search_query = request.GET.get('search', '')
    food_category = request.GET.get('category', '')

    recipes = Recipe.objects.all()

    if search_query:
        recipes = recipes.filter(title__icontains=search_query)

    if food_category:
        recipes = recipes.filter(food_category=food_category)

    categories = Recipe.FOOD_NAME_CHOICES

    return render(request, 'blog/recipe_list.html', {
        'recipes': recipes,
        'search_query': search_query,
        'categories': categories,
        'selected_category': food_category,
    })

def blog_detail(request, pk):
    blog_post = get_object_or_404(BlogPost, pk=pk)
    comments = Comment.objects.filter(blog_post=blog_post)

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.blog_post = blog_post
            comment.author = request.user
            comment.save()
            return redirect('blog_detail', pk=blog_post.pk)
    else:
        form = CommentForm()

    return render(request, 'blog/blog_detail.html', {
        'blog_post': blog_post,
        'comments': comments,
        'form': form
    })


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the user and trigger the save method in your form
            login(request, user)  # Automatically log the user in after registration
            return redirect('home')  # Redirect to a home or dashboard page
    else:
        form = RegistrationForm()

    return render(request, 'registration/register.html', {'form': form})

@login_required
def my_account(request):
    saved_recipes = request.user.saved_recipes.all()
    saved_posts = request.user.saved_posts.all()
    user_comments = Comment.objects.filter(author=request.user)
    return render(request, 'blog/my_account.html', {
        'saved_recipes': saved_recipes,
        'saved_posts': saved_posts,
        'user_comments': user_comments
    })

@login_required
def save_recipe(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    recipe.saved_by.add(request.user)
    return redirect('recipe_detail', pk=pk)

@login_required
def save_post(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    post.saved_by.add(request.user)
    return redirect('blog_detail', pk=pk)


def home(request):
    return render(request, 'blog/home.html')

@login_required
def edit_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.user != comment.author:
        return redirect('my_account')

    if request.method == "POST":
        if 'delete' in request.POST:
            comment.delete()
            next_url = request.POST.get('next', reverse('my_account'))
            return redirect(next_url)
        else:
            form = CommentForm(request.POST, instance=comment)
            if form.is_valid():
                form.save()
                next_url = request.POST.get('next', reverse('my_account'))
                return redirect(next_url)
    else:
        form = CommentForm(instance=comment)
        next_url = request.GET.get('next', reverse('my_account'))

    return render(request, 'blog/edit_comment.html', {
        'form': form,
        'next': next_url
    })

@login_required
def like_post(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return redirect('blog_detail', pk=pk)

import csv
import xml.etree.ElementTree as ET
from django.http import HttpResponse
from .models import Comment

def export_comments_xml(request):
    comments = Comment.objects.filter(author=request.user)
    root = ET.Element("comments")

    for comment in comments:
        comment_element = ET.SubElement(root, "comment")
        ET.SubElement(comment_element, "content").text = comment.content
        ET.SubElement(comment_element, "created_at").text = comment.created_at.isoformat()
        ET.SubElement(comment_element, "author").text = comment.author.username
        if comment.recipe:
            ET.SubElement(comment_element, "recipe").text = comment.recipe.title
        if comment.blog_post:
            ET.SubElement(comment_element, "blog_post").text = comment.blog_post.title

    tree = ET.ElementTree(root)
    response = HttpResponse(content_type='application/xml')
    response['Content-Disposition'] = 'attachment; filename="comments.xml"'
    tree.write(response, encoding='utf-8', xml_declaration=True)
    return response

import xlwt
from django.http import HttpResponse

def export_comments_xls(request):
    comments = Comment.objects.filter(author=request.user)
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="comments.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Comments')

    # Column headers
    columns = ['Content', 'Created At', 'Author', 'Recipe', 'Blog Post']
    for col_num, column_title in enumerate(columns):
        ws.write(0, col_num, column_title)

    # Data rows
    for row_num, comment in enumerate(comments, start=1):
        recipe_title = comment.recipe.title if comment.recipe else ''
        blog_title = comment.blog_post.title if comment.blog_post else ''
        row = [comment.content, comment.created_at, comment.author.username, recipe_title, blog_title]
        for col_num, cell_value in enumerate(row):
            ws.write(row_num, col_num, str(cell_value))

    wb.save(response)
    return response
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import BlogPost, Recipe, Comment, Rating
from .forms import CommentForm, RecipeRatingForm


class BlogViewsTestCase(TestCase):
    def setUp(self):
        # Setup client and test user
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.blog_post = BlogPost.objects.create(title='Test Blog', content='Test Content', author=self.user)
        self.recipe = Recipe.objects.create(title='Test Recipe', description='Test Description', author=self.user)
        self.comment = Comment.objects.create(content='Test Comment', author=self.user, blog_post=self.blog_post)

    def test_blog_list_view(self):
        response = self.client.get(reverse('blog_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/blog_list.html')

    def test_recipe_detail_view(self):
        response = self.client.get(reverse('recipe_detail', args=[self.recipe.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/recipe_detail.html')

    def test_blog_detail_view(self):
        response = self.client.get(reverse('blog_detail', args=[self.blog_post.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/blog_detail.html')

    def test_register_view(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')

    def test_my_account_view(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('my_account'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/my_account.html')

    def test_save_recipe_view(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('save_recipe', args=[self.recipe.pk]))
        self.assertEqual(response.status_code, 302)  # Redirect after saving
        self.assertIn(self.user, self.recipe.saved_by.all())

    def test_save_post_view(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('save_post', args=[self.blog_post.pk]))
        self.assertEqual(response.status_code, 302)  # Redirect after saving
        self.assertIn(self.user, self.blog_post.saved_by.all())

    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/home.html')

    def test_like_post_view(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('like_post', args=[self.blog_post.pk]))
        self.assertEqual(response.status_code, 302)  # Redirect after liking
        self.assertIn(self.user, self.blog_post.likes.all())

        # Test unlike functionality
        response = self.client.post(reverse('like_post', args=[self.blog_post.pk]))
        self.assertEqual(response.status_code, 302)  # Redirect after unliking
        self.assertNotIn(self.user, self.blog_post.likes.all())

    def test_comment_on_blog_post(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('blog_detail', args=[self.blog_post.pk]), data={'content': 'Test Comment'})
        self.assertEqual(response.status_code, 302)  # Redirect after comment
        self.assertEqual(Comment.objects.count(), 2)  # 1 initial comment, 1 from the post

    def test_comment_on_recipe(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('recipe_detail', args=[self.recipe.pk]), data={'content': 'Test Comment'})
        self.assertEqual(response.status_code, 302)  # Redirect after comment
        self.assertEqual(Comment.objects.count(), 2)  # 1 initial comment, 1 from the post

    #def test_recipe_rating(self):
     #   self.client.login(username='testuser', password='12345')
      #  response = self.client.post(reverse('recipe_detail', args=[self.recipe.pk]), data={'rating': 5})
        #self.assertEqual(response.status_code, 302)  # Redirect after rating
       # self.assertEqual(Rating.objects.count(), 1)  # Check if the rating was saved
        #self.assertEqual(self.recipe.average_rating, 5)  # Ensure the rating is correctly calculated

    def test_edit_comment(self):
        self.client.login(username='testuser', password='12345')
        # Test editing the comment
        comment = Comment.objects.create(content='Old Comment', author=self.user, blog_post=self.blog_post)
        response = self.client.post(reverse('edit_comment', args=[comment.pk]), data={'content': 'Updated Comment'})
        self.assertEqual(response.status_code, 302)  # Redirect after editing
        comment.refresh_from_db()
        self.assertEqual(comment.content, 'Updated Comment')

    def test_delete_comment(self):
        self.client.login(username='testuser', password='12345')
        # Test deleting the comment
        comment = Comment.objects.create(content='Old Comment', author=self.user, blog_post=self.blog_post)
        response = self.client.post(reverse('edit_comment', args=[comment.pk]), data={'delete': 'true'})
        self.assertEqual(response.status_code, 302)  # Redirect after deletion
        self.assertEqual(Comment.objects.count(), 1)  # Only the original comment remains

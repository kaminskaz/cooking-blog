from django.conf.urls.static import static
from django.urls import path

from final_project import settings
from final_project.settings import BASE_DIR
from . import views
from django.contrib.auth import views as auth_views

from .views import blog_detail, like_post

urlpatterns = [
    path('home/', views.home, name='home'),
    path('recipes/', views.recipe_list, name='recipe_list'),
    path('recipes/<int:pk>/', views.recipe_detail, name='recipe_detail'),
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<int:pk>/', views.blog_detail, name='blog_detail'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('register/', views.register, name='register'),
    path('logout/', auth_views.LogoutView.as_view(next_page='recipe_list'), name='logout'),
    path('my_account/', views.my_account, name='my_account'),
    path('comment/<int:pk>/edit/', views.edit_comment, name='edit_comment'),
    path('recipes/<int:pk>/save/', views.save_recipe, name='save_recipe'),
    path('blog/<int:pk>/save/', views.save_post, name='save_post'),
    path('post/<int:pk>/', blog_detail, name='blog_detail'),
    path('post/<int:pk>/like/', like_post, name='like_post'),
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
path('export_comments/xml/', views.export_comments_xml, name='export_comments_xml'),
    path('export_comments/excel/', views.export_comments_xls, name='export_comments_excel'),
]

import os

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
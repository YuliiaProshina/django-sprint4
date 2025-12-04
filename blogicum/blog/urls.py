from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('category/<slug:category_slug>/', views.category_posts,
         name='category_posts'),

    path('create/', views.PostCreateView.as_view(), name='create_post'),
    path('profile/<str:username>/', views.ProfileDetailView.as_view(), name='profile'),  
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='edit_profile'),  
]

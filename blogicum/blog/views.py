from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from .models import Post, Category
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin

User = get_user_model()


def index(request):
    """Рендеринг главной страницы."""
    post_list = Post.objects.filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    ).order_by('-pub_date')[:5]
    context = {
        'post_list': post_list
    }
    return render(request, 'blog/index.html', context)


def post_detail(request, post_id):
    """Рендеринг страницы статьи."""
    post = get_object_or_404(
        Post.objects.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True),
        pk=post_id
    )
    context = {
        'post': post
    }
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    """Рендеринг статьи по категории."""
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    posts = Post.objects.filter(
        category=category.id,
        is_published=True,
        pub_date__lte=timezone.now()
    ).order_by('-pub_date')

    context = {
        'category': category,
        'post_list': posts
    }
    return render(request, 'blog/category.html', context)


class PostCreateView(CreateView):
    model = Post
    tempate_name = 'blog/create.html'
    fields = '__all__'


class ProfileDetailView(DetailView):
    model = User
    template_name = 'blog/profile.html'

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_object()
        context['profile'] = profile
        context['request'] = self.request

        return context


class ProfileUpdateView(UpdateView):
    model = User
    template_name = 'blog/user.html'

    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={
            'username': self.request.user.username})

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])

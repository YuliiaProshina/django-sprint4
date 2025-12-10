from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .constants import PAGINATION_COUNT
from .forms import CommentForm, PostForm
from .mixins import OnlyAuthorMixin
from .models import Category, Comment, Post
from .service import get_posts_queryset

User = get_user_model()


class IndexListView(ListView):
    """Отображение главной страницы."""

    model = Post
    template_name = 'blog/index.html'
    paginate_by = PAGINATION_COUNT

    def get_queryset(self):
        return get_posts_queryset()


class PostDetailView(DetailView):
    """Отображение страницы поста."""

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self):
        post = super().get_object()
        user = self.request.user
        is_author = user.is_authenticated and user == post.author
        is_public = (
            post.is_published
            and post.category.is_published
            and post.pub_date <= timezone.now()
        )
        if is_author or is_public:
            return post
        raise Http404('Пост не найден')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related(
            'author')
        return context


class CategoryPostsView(ListView):
    """Отображение постов по категориям."""

    model = Post
    template_name = 'blog/category.html'
    paginate_by = PAGINATION_COUNT

    def get_category(self):
        return get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )

    def get_queryset(self):
        category = self.get_category()
        return get_posts_queryset(
            base_queryset=category.posts.all()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_category()
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание поста."""

    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile', kwargs={
            'username': self.request.user.username
        })


class PostUpdateView(OnlyAuthorMixin, UpdateView):
    """Редактирование поста."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.object.id})


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    """Удаление поста."""

    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'
    success_url = reverse_lazy('blog:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context


class ProfileDetailView(DetailView):
    """Отображение профиля пользователя."""

    model = User
    template_name = 'blog/profile.html'
    context_object_name = 'profile'

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.object
        posts = get_posts_queryset(base_queryset=profile.posts.all(),
                                   apply_filter=self.request.user != profile)
        paginator = Paginator(posts, PAGINATION_COUNT)
        page_number = self.request.GET.get('page')
        context['page_obj'] = paginator.get_page(page_number)
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля пользователя."""

    model = User
    template_name = 'blog/user.html'
    fields = ('first_name', 'last_name', 'email', )

    def get_success_url(self):
        return reverse('blog:profile', kwargs={
            'username': self.request.user.username})

    def get_object(self):
        return self.request.user


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Создание комментариев."""

    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        form.instance.post = post
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})


class CommentUpdateView(LoginRequiredMixin, OnlyAuthorMixin, UpdateView):
    """Редактирование комментария."""

    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={
            'post_id': self.kwargs['post_id']
        })


class CommentDeleteView(LoginRequiredMixin, OnlyAuthorMixin, DeleteView):
    """Удаление комментария."""

    model = Comment
    template_name = 'blog/comment.html'
    success_url = reverse_lazy('blog:detail')
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={
            'post_id': self.kwargs['post_id']
        })

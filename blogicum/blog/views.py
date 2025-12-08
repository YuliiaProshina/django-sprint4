from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .forms import CommentForm, PostForm
from .models import Category, Comment, Post

User = get_user_model()


class OnlyAuthorMixin(UserPassesTestMixin):
    """Проверка, что пользователь является автором"""

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user

    def handle_no_permission(self):
        return redirect(reverse('blog:post_detail',
                                kwargs={'post_id': self.get_object().id}))


class IndexListView(ListView):
    """Отображение главной страницы"""

    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        ).annotate(comment_count=Count('comments')).order_by('-pub_date')


class PostDetailView(DetailView):
    """Отображение страницы поста"""

    model = Post
    template_name = 'blog/detail.html'
    ordering = '-pub_date'
    paginate_by = 10

    def get_object(self):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        if (
            self.request.user.is_authenticated
            and self.request.user == post.author
        ):
            return post

        if (
            post.is_published
            and post.category.is_published
            and post.pub_date <= timezone.now()
        ):
            return post
        raise Http404('Пост не найден')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.order_by('created_at')
        return context


class CategoryPostsView(ListView):
    """Отображение постов по категориям"""

    model = Post
    template_name = 'blog/category.html'
    paginate_by = 10
    context_object_name = 'posts'

    def get_queryset(self):
        category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return Post.objects.filter(
            category=category,
            is_published=True,
            pub_date__lte=timezone.now()
        ).annotate(comment_count=Count('comments')).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание поста"""

    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        if form.cleaned_data['pub_date'] < timezone.now():
            form.instance.pub_date = timezone.now()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={
            'username': self.request.user.username
        })


class PostUpdateView(OnlyAuthorMixin, UpdateView):
    """Редактирование поста"""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def clean_pub_date(self):
        pub_date = self.cleaned_data.get('pub_date')
        if pub_date and pub_date < timezone.now():
            raise forms.ValidationError(
                'Дата публикации не может быть в прошлом.'
            )
        return pub_date

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.object.id})


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    """Удаление поста"""

    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'
    success_url = reverse_lazy('blog:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context


class ProfileDetailView(DetailView):
    """Отображение профиля пользователя"""

    model = User
    template_name = 'blog/profile.html'
    context_object_name = 'profile'

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.object
        if self.request.user == profile:
            posts = Post.objects.filter(author=profile).annotate(
                comment_count=Count('comments')).order_by('-pub_date')
        else:
            posts = Post.objects.filter(
                author=profile,
                is_published=True,
                pub_date__lte=timezone.now(),
                category__is_published=True,
            ).annotate(comment_count=Count('comments')).order_by('-pub_date') 
        paginator = Paginator(posts, 10)
        page_number = self.request.GET.get('page')
        context['page_obj'] = paginator.get_page(page_number)
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля пользователя"""

    model = User
    template_name = 'blog/user.html'
    fields = ('first_name', 'last_name', 'email', )

    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={
            'username': self.request.user.username})

    def get_object(self):
        return self.request.user


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Создание комментариев"""

    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.post_obj = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_obj
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.post_obj.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        return context


class CommentUpdateView(LoginRequiredMixin, OnlyAuthorMixin, UpdateView):
    """Редактирование комментария"""

    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={
            'post_id': self.kwargs['post_id']
        })


class CommentDeleteView(OnlyAuthorMixin, LoginRequiredMixin, DeleteView):
    """Удаление комментария"""

    model = Comment
    template_name = 'blog/comment.html'
    success_url = reverse_lazy('blog:detail')
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={
            'post_id': self.kwargs['post_id']
        })

from django.contrib import admin

from .models import Category, Comment, Location, Post

empty_value_display = 'Не задано'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'slug', 'is_published')
    search_fields = ('title',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published')
    search_fields = ('name',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'text', 'pub_date', 'author', 'location',
                    'category', 'is_published')
    search_fields = ('title', 'pub_date', 'author__username', 'location__name',
                     'category__title')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('text', 'author',)
    search_fields = ('text', 'author__username',)

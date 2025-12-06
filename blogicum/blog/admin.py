from django.contrib import admin

from .models import Category, Location, Post

empty_value_display = 'Не задано'


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'slug', 'is_published')
    search_fields = ('title',)


class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published')
    search_fields = ('name',)


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'text', 'pub_date', 'author', 'location',
                    'category', 'is_published')
    search_fields = ('title', 'pub_date', 'author', 'location', 'category')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)

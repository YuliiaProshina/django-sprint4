from django.contrib import admin

from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pages/', include(('pages.urls', 'pages'), namespace='pages')),
    path('', include(('blog.urls', 'blog'), namespace='blog')),
]

from django.db.models import Count
from django.utils import timezone

from .models import Post


def get_posts_queryset(base_queryset=None, apply_filter=True,
                       annotate_comments=True):
    """Возвращает QuerySet постов.

    Параметры:
    base_queryset: начальный сет,
    apply_filter: отфильтровать опубликованные посты,
    annotate_comments: посчитать количество комментариев.
    """
    query_set = (base_queryset or Post.objects).select_related(
        'author', 'category', 'location')
    if apply_filter:
        query_set = query_set.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now(),
        )
    if annotate_comments:
        query_set = query_set.annotate(comment_count=Count('comments'))

    return query_set.order_by('-pub_date')

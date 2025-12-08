from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse


class OnlyAuthorMixin(UserPassesTestMixin):
    """Проверка, что пользователь является автором."""

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user

    def handle_no_permission(self):
        return redirect(reverse('blog:post_detail',
                                kwargs={'post_id': self.get_object().id}))

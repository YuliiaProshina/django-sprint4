from django import forms

from .models import Comment, Post


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea({'rows': 5, 'cols': 30})
        }


class PostForm(forms.ModelForm):
    pub_date = forms.DateTimeField(
        label='Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем — '
            'можно делать отложенные публикации.'),
        input_formats=['%Y-%m-%d %H:%M'],
        widget=forms.DateTimeInput(
            format='%Y-%m-%d %H:%M',
            attrs={'type': 'datetime-local'}
        ),
    )

    class Meta:
        model = Post
        exclude = ('author', )

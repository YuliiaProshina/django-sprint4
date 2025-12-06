from .models import Comment, Post
from django import forms 
from django.utils import timezone

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)


class PostForm(forms.ModelForm):
    pub_date = forms.DateTimeField(
        input_formats=['%Y-%m-%d %H:%M'],
        widget=forms.DateTimeInput(
            format='%Y-%m-%d %H:%M',
            attrs={'type': 'datetime-local'}
        )
    )

    def clean_pub_date(self):
        pub_date = self.cleaned_data.get('pub_date')
        if pub_date and pub_date < timezone.now():
            raise forms.ValidationError(
                'Дата публикации не может быть в прошлом.'
            )
        return pub_date

    class Meta:
        model = Post
        fields = ('title', 'text', 'location', 'image', 'pub_date', 'category')

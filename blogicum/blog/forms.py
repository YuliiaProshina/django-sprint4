from .models import Comment, Post
from django import forms 


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
        
    class Meta:
        model = Post    
        fields = ('title', 'text', 'location', 'image', 'pub_date', 'category', )  
             
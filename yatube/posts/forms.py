from django.forms import ModelForm

from .models import Post, Comment


class PostForm(ModelForm):
    """Форма для создания и редактирования поста."""

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')


class CommentForm(ModelForm):
    """Форма для создания и редактирования поста."""

    class Meta:
        model = Comment
        fields = ('text',)

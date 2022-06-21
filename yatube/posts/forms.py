from django.forms import ModelForm

from .models import Post


class PostForm(ModelForm):
    """Форма для создания и редактирования поста."""

    class Meta:
        model = Post
        fields = ('text', 'group')

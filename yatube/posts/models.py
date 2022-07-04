from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    """Группы для объединения постов."""

    title = models.CharField('Название группы', max_length=200, unique=True)
    slug = models.SlugField('Уникальный url', unique=True)
    description = models.TextField('Описание группы')

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title


class Post(models.Model):
    """Посты размещенные пользователями."""

    text = models.TextField('Текст поста', help_text='Текст нового поста')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='posts', verbose_name='Автор')
    group = models.ForeignKey(
        Group, on_delete=models.SET_NULL,
        related_name='group_posts',
        verbose_name='Группа',
        blank=True, null=True,
        help_text='Группа, к которой будет относиться пост')
    image = models.ImageField('Картинка', upload_to='posts/',
                              blank=True)

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    """Комментарии к постам."""
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='post', verbose_name='Пост')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='author', verbose_name='Автор')
    text = models.TextField('Текст комментария', help_text='Текст комментария')
    created = models.DateTimeField('Дата комментария', auto_now_add=True)

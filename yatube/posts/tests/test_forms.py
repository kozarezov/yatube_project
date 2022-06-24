from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):
    """Тест view приложения posts."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )

    def setUp(self):
        """Создаем неавторизованного и авторизованного пользователя."""
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_forms_create(self):
        """Cоздаётся новая запись в базе данных."""
        count_posts = Post.objects.count()
        form_fields = {
            'text': 'Тестовый пост 1',
            'group': self.group.id,
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_fields
        )

        self.assertRedirects(response, reverse(
                             'posts:profile', kwargs={'username': self.user}))
        self.assertEqual(Post.objects.count(), count_posts + 1)
        self.assertTrue(Post.objects.filter(text=form_fields['text']).
                        filter(group=form_fields['group']).
                        filter(author=self.user).exists())

    def test_forms_edit(self):
        """Можно изменить существующую запись."""
        count_posts = Post.objects.count()
        form_fields = {
            'text': 'Измененный пост',
            'group': self.group.id,
        }

        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}),
            data=form_fields
        )

        self.assertRedirects(response, reverse('posts:post_detail',
                             kwargs={'post_id': self.post.id}))
        self.assertEqual(Post.objects.count(), count_posts)
        self.assertTrue(Post.objects.filter(text=form_fields['text']).
                        filter(group=form_fields['group']).
                        filter(author=self.user).exists())

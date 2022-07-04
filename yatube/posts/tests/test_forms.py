import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post, Comment

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
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
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

    @classmethod
    def tearDownClass(cls):
        """Удаляем директорию и всё её содержимое."""
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

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

    def test_forms_image(self):
        """Проверка добавления изображения."""
        count_posts = Post.objects.count()
        form_fields = {
            'text': 'Тестовый пост 2',
            'image': self.uploaded
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_fields
        )

        self.assertTrue(Post.objects.filter(image='posts/small.gif').exists())
        self.assertRedirects(response, reverse(
                             'posts:profile', kwargs={'username': self.user}))
        self.assertEqual(Post.objects.count(), count_posts + 1)

    def test_forms_create_comments_authorized(self):
        """Создается запись comments в базе данных."""
        count = Comment.objects.count()
        form_fields = {
            'text': 'Тестовый коментарий',
        }

        response = self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': self.post.id}),
            data=form_fields
        )

        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(Comment.objects.count(), count + 1)
        self.assertTrue(Comment.objects.filter(text=form_fields['text']).
                        filter(author=self.user).
                        filter(post=self.post).exists())

    def test_forms_create_comments_guest(self):
        """Не создает запись, если пользователь не авторизован."""
        count = Comment.objects.count()
        form_fields = {
            'text': 'Тестовый коментарий',
        }
        url = reverse('posts:add_comment', kwargs={'post_id': self.post.id})

        response_guest = self.guest_client.post(url, data=form_fields)

        self.assertRedirects(response_guest,
                             f'/auth/login/?next={url}')
        self.assertNotEqual(Post.objects.count(), count)
        self.assertFalse(Post.objects.filter(
                         text=form_fields['text']).exists())

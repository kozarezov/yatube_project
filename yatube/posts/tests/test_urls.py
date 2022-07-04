from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    """Тест URL приложения posts."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_1 = User.objects.create_user(username='auth_1')
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
        cls.post_1 = Post.objects.create(
            author=cls.user_1,
            text='Тестовый пост 1',
            group=cls.group
        )

    def setUp(self):
        """Создаем неавторизованного и авторизованного пользователя."""
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_exists_authorized(self):
        """Проверка доступности страниц для авторизованного пользователя."""
        urls_and_templates = {
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
        }

        for address, template in urls_and_templates.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                response_guest = self.guest_client.get(address)

                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)
                self.assertRedirects(response_guest,
                                     f'/auth/login/?next={address}')

    def test_urls_exists_non_authorized(self):
        """Проверка доступности страниц для неавторизованного пользователя."""
        urls_and_templates = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
        }

        for address, template in urls_and_templates.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)

                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_urls_redirect_another_autor(self):
        """Проверка доступа к редактированию поста другого автора."""
        response = self.authorized_client.get(f'/posts/{self.post_1.id}/edit/')

        self.assertRedirects(response, f'/posts/{self.post_1.id}/')

    def test_urls_unexisting_page(self):
        """Проверка доступа к несуществующей странице."""
        response = self.guest_client.get('/unexisting_page/')

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_comment_redirect_anonymous(self):
        """Проверка доступа к комментированию поста неавторизованного."""
        url = f'/posts/{self.post.id}/comment/'
        response_guest = self.guest_client.get(url)

        self.assertRedirects(response_guest,
                             f'/auth/login/?next={url}')

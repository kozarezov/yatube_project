from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UserURLTests(TestCase):
    """Тест URL приложения users."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

    def setUp(self):
        """Создаем неавторизованного и авторизованного пользователя."""
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_exists_authorized(self):
        """Проверка доступности страниц для авторизованного пользователя."""
        urls_and_templates = {
            reverse('users:password_change_form'):
            'users/password_change_form.html',
            reverse('users:password_change_done'):
            'users/password_change_done.html',
            reverse('users:logout'): 'users/logged_out.html',
        }
        for address, template in urls_and_templates.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_urls_exists_non_authorized(self):
        """Проверка доступности страниц для неавторизованного пользователя."""
        urls_and_templates = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
            reverse('users:password_reset_form'):
            'users/password_reset_form.html',
            reverse('users:password_reset_done'):
            'users/password_reset_done.html',
            reverse('users:password_reset_confirm',
                    kwargs={'uidb64': '1', 'token': '123qwerty'}):
            'users/password_reset_confirm.html',
            reverse('users:password_reset_complete'):
            'users/password_reset_complete.html',
        }
        for address, template in urls_and_templates.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_urls_redirect_non_authorized(self):
        """Страницы перенаправляют неавторизованного пользователя."""
        urls = [
            reverse('users:password_change_form'),
            reverse('users:password_change_done')
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

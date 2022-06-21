from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UserFormTests(TestCase):
    """Тест Form приложения users."""
    def setUp(self):
        """Создаем неавторизованного пользователя."""
        self.guest_client = Client()

    def test_create_user(self):
        """Cоздаётся новая запись в базе данных."""
        user_count = User.objects.count()
        form_data = {
            'first_name': 'user_test',
            'last_name': 'user_test',
            'username': 'user_test',
            'email': 'user_test@test.ru',
            'password1': '123qwertyTEST',
            'password2': '123qwertyTEST',
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
        )
        self.assertRedirects(
            response,
            reverse('posts:index')
        )
        self.assertEqual(User.objects.count(), user_count + 1)
        self.assertTrue(User.objects.get(username='user_test'))

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class PostViewTests(TestCase):
    """Тест view приложения posts."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.users = []
        cls.groups = []
        cls.posts = []
        for i in range(2):
            cls.users.append(User.objects.create_user(username=f'auth_{i}'))
            cls.groups.append(
                Group.objects.create(
                    title=f'Тестовая группа {i}',
                    slug=f'test_{i}',
                    description=f'Тестовое описание {i}',
                ))
            cls.posts.append(
                Post.objects.create(
                    author=cls.users[i],
                    group=cls.groups[i],
                    text=f'{i}'
                ))

    def setUp(self):
        """Создаем авторизованного пользователя."""
        self.authorized_client = Client()
        self.authorized_client.force_login(self.users[0])

    def test_views_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        urls_and_templates = {
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': '1'}):
            'posts/create_post.html',
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.groups[0].slug}):
            'posts/group_list.html',
            reverse('posts:post_detail', kwargs={'post_id': '1'}):
            'posts/post_detail.html',
            reverse('posts:profile',
                    kwargs={'username': self.users[0].username}):
            'posts/profile.html',
        }
        for address, template in urls_and_templates.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_views_context(self):
        """Шаблоны сформированы с правильным контекстом."""
        urls = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.groups[0].slug}),
            reverse('posts:profile',
                    kwargs={'username': self.users[0].username})
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                post_array = response.context['page_obj']
                for post in post_array:
                    # Закостылил, т.к. не получилось узнать индекс поста
                    i = int(post.text)
                    self.assertEqual(post.author.username,
                                     self.posts[i].author.username)
                    self.assertEqual(post.text, self.posts[i].text)
                    self.assertEqual(post.group.title,
                                     self.posts[i].group.title)

    def test_views_in_page(self):
        """Посты на верных страницах."""
        must_be = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.groups[0].slug}),
            reverse('posts:profile',
                    kwargs={'username': self.users[0].username}),
        ]
        must_not_be = [
            reverse('posts:group_list', kwargs={'slug': self.groups[1].slug}),
            reverse('posts:profile',
                    kwargs={'username': self.users[1].username}),
        ]
        for url in must_be:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertIn(self.posts[0], response.context['page_obj'])
        for url in must_not_be:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertNotIn(self.posts[0], response.context['page_obj'])

    def test_views_detail_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        for i in range(0, len(self.posts)):
            url = reverse('posts:post_detail',
                          kwargs={'post_id': self.posts[i].id})
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.context['post'].author.username,
                                 self.users[i].username)
                self.assertEqual(response.context['post'].text,
                                 self.posts[i].text)

    def test_views_create_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_views_edit_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        url = reverse('posts:post_edit',
                      kwargs={'post_id': self.posts[0].id})
        response = self.authorized_client.get(url)
        self.assertEqual(response.context['post'].author.username,
                         self.users[0].username)
        self.assertEqual(response.context['post'].text,
                         self.posts[0].text)
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields.get(value)
                self.assertIsInstance(form_field, expected)


class PostViewPaginatorTests(TestCase):
    """Тест пагинатора приложения posts."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание')
        cls.posts = []
        for i in range(13):
            cls.posts.append(
                Post.objects.create(
                    author=cls.user,
                    group=cls.group,
                    text=f'{i}'
                ))

    def setUp(self):
        """Создаем авторизованного пользователя."""
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_views_context(self):
        """Шаблоны сформирован с правильным пагинатором."""
        urls = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile',
                    kwargs={'username': self.user.username})
        ]
        for url in urls:
            with self.subTest(url=url):
                response_1 = self.authorized_client.get(url)
                response_2 = self.authorized_client.get(
                    url + '?page=2')
                self.assertEqual(
                    len(response_1.context['page_obj']),
                    settings.POSTS_PER_PAGE)
                self.assertEqual(
                    len(response_2.context['page_obj']),
                    len(self.posts) - settings.POSTS_PER_PAGE)

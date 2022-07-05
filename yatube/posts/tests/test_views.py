import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.cache import cache

from posts.models import Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewTests(TestCase):
    """Тест view приложения posts."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
            group=cls.group,
            image=cls.uploaded
        )
        cls.post_1 = Post.objects.create(
            author=cls.user_1,
            text='Тестовый пост 1',
            image=cls.uploaded
        )
        cls.post_create_url = reverse('posts:post_create')
        cls.index_url = reverse('posts:index')
        cls.group_url = reverse('posts:group_list',
                                kwargs={'slug': cls.group.slug})
        cls.profile_url = reverse('posts:profile',
                                  kwargs={'username': cls.user.username})
        cls.post_detail_url = reverse('posts:post_detail',
                                      kwargs={'post_id': '1'})
        cls.post_edit_url = reverse('posts:post_edit',
                                    kwargs={'post_id': '1'})

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        """Создаем авторизованного пользователя."""
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_views_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        urls_and_templates = {
            self.post_create_url: 'posts/create_post.html',
            self.post_edit_url: 'posts/create_post.html',
            self.index_url: 'posts/index.html',
            self.group_url: 'posts/group_list.html',
            self.post_detail_url: 'posts/post_detail.html',
            self.profile_url: 'posts/profile.html',
        }

        for address, template in urls_and_templates.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)

                self.assertTemplateUsed(response, template)

    def test_views_index_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.index_url)
        first_post = response.context['page_obj'].object_list[0]

        self.assertEqual(first_post.author, self.user_1)
        self.assertEqual(first_post, self.post_1)

    def test_views_context(self):
        """Шаблоны group и profile сформированы с правильным контекстом."""
        urls = {
            self.group_url,
            self.profile_url
        }

        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                first_post = response.context['page_obj'].object_list[0]

                self.assertEqual(first_post.author,
                                 self.user)
                self.assertEqual(first_post.group,
                                 self.group)
                self.assertEqual(first_post, self.post)

    def test_views_in_page(self):
        """Посты на верных страницах."""
        urls = {
            self.group_url,
            self.profile_url,
        }

        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)

                self.assertIn(self.post, response.context['page_obj'])
                self.assertNotIn(self.post_1, response.context['page_obj'])

    def test_views_detail_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.post_detail_url)

        self.assertEqual(response.context['post'].author, self.user)
        self.assertEqual(response.context['post'], self.post)

    def test_views_create_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.post_create_url)
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

        response = self.authorized_client.get(self.post_edit_url)
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields.get(value)

                self.assertIsInstance(form_field, expected)
        self.assertEqual(response.context['post'].author, self.user)
        self.assertEqual(response.context['post'], self.post)

    def test_views_context_with_image(self):
        """Шаблоны c изображением сформированы с правильным контекстом."""
        urls = {
            self.index_url,
            self.group_url,
            self.profile_url,
            self.post_detail_url
        }

        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                if response.context.get('page_obj'):
                    self.assertTrue(response.context['page_obj'][0].image)
                else:
                    self.assertTrue(response.context['post'].image)

    def test_views_cashed(self):
        """Содержимое главной страницы кэшируется."""
        response = self.authorized_client.get(self.index_url)
        Post.objects.all().delete()
        response_after_delete = self.authorized_client.get(self.index_url)

        self.assertEqual(response.content, response_after_delete.content)

        cache.clear()
        response_after_clear = self.authorized_client.get(self.index_url)

        self.assertNotEqual(response.content, response_after_clear.content)


class PostViewPaginatorTests(TestCase):
    """Тест пагинатора приложения posts."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.COUNT_TEST_POST = 13
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание')
        for new_post_num in range(cls.COUNT_TEST_POST):
            Post.objects.create(
                author=cls.user,
                group=cls.group,
                text=f'Тестовый текст {new_post_num}'
            )

    def setUp(self):
        """Создаем авторизованного пользователя."""
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_views_context(self):
        """Шаблоны сформирован с правильным пагинатором."""
        remains_post_count = Post.objects.count() - settings.POSTS_PER_PAGE
        urls = {
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile',
                    kwargs={'username': self.user.username})
        }

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
                    remains_post_count)

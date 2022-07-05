from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm, CommentForm
from .models import Group, Post, Comment, Follow
from .utils import paginate_pls

User = get_user_model()


def index(request):
    """Главная страница записей."""
    post_list = Post.objects.select_related('group', 'author').all()
    context = {
        'page_obj': paginate_pls(request, post_list),
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Возвращает посты, отфильтрованные по группам."""
    group = get_object_or_404(Group, slug=slug)
    post_list = group.group_posts.all()
    context = {
        'page_obj': paginate_pls(request, post_list),
        'group': group,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Страница профайла пользователя."""
    post_author = get_object_or_404(User, username=username)
    post_list = (Post.objects.select_related('group', 'author')
                 .filter(author__username=username))
    post_count = post_list.count()
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=post_author).exists()
    context = {
        'page_obj': paginate_pls(request, post_list),
        'post_count': post_count,
        'post_author': post_author,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Страница для просмотра отдельного поста."""
    post = Post.objects.select_related('group', 'author').get(pk=post_id)
    post_count = Post.objects.filter(author__username=post.author).count()
    comments = Comment.objects.filter(post_id=post_id).select_related('author')
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'post_count': post_count,
        'comments': comments,
        'form': form
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Страница для создания поста."""
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect('posts:profile', username=request.user.username)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    """Страница для редактирования поста."""
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        post.save()
        return redirect('posts:post_detail', post_id)
    return render(request, 'posts/create_post.html',
                  {'form': form, 'post': post, 'is_edit': True})


@login_required
def add_comment(request, post_id):
    """Комментирование поста."""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Получение постов авторов в подписках из базы данных."""
    post_list = (Post.objects.select_related('group', 'author').
                 filter(author__following__user=request.user))
    context = {
        'page_obj': paginate_pls(request, post_list),
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Подписаться на автора."""
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    """Отписаться от автора."""
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:profile', username=username)

from django.shortcuts import render, get_object_or_404
from .models import Post, Group


def index(request):
    """Главная страница записей."""
    template = 'posts/index.html'
    posts = Post.objects.order_by('-pub_date')[:10]
    # В словаре context отправляем информацию в шаблон
    context = {
        'title': 'Это главная страница проекта Yatube',
        'posts': posts,
    }
    return render(request, template, context)


def group_posts(request, slug):
    """Возвращает посты, отфильтрованные по группам."""
    group = get_object_or_404(Group, slug=slug)
    template = 'posts/group_list.html'
    posts = Post.objects.filter(group=group).order_by('-pub_date')[:10]
    context = {
        'title': 'Здесь будет информация о группах проекта Yatube',
        'group': group,
        'posts': posts,
    }
    return render(request, template, context)

import imp
from django.shortcuts import render
from .models import Post


# Create your views here.
def index(request):
    """Главная страница записей."""
    template = 'posts/index.html'
    posts = Post.objects.order_by('-pub_date')[:10]
    # В словаре context отправляем информацию в шаблон
    context = {
        'posts': posts,
    }
    return render(request, template, context)


def group_posts(request, slug):
    """Возвращает посты, отфильтрованные по группам."""
    template = 'posts/group_list.html'
    title = "Здесь будет информация о группах проекта Yatube"
    context = {
        'title': title,
    }
    return render(request, template, context)

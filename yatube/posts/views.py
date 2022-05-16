from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def index(request):
    """Главная страница записей."""
    return HttpResponse('Главная страница')


def group_posts(request, slug):
    """Возвращает посты, отфильтрованные по группам."""
    return HttpResponse(f'Страница для группы {slug}')

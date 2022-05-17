from django.shortcuts import render


# Create your views here.
def index(request):
    """Главная страница записей."""
    template = 'posts/index.html'
    return render(request, template)


def group_posts(request, slug):
    """Возвращает посты, отфильтрованные по группам."""
    template = 'posts/group_list.html'
    return render(request, template)

from django.conf import settings
from django.core.paginator import Paginator


def paginate_pls(request, post_list):
    """Функция для создания пагинации Post на странице."""
    paginator = Paginator(post_list, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj

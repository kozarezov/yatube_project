from django.contrib import admin
# Из модуля models импортируем модель Post
from .models import Post, Group


class PostAdmin(admin.ModelAdmin):
    # Перечисляем поля, которые должны отображаться в админке
    list_display = ('pk', 'text', 'pub_date', 'author', "group")
    # Добавляем интерфейс для поиска по тексту постов
    search_fields = ('text',)
    # Добавляем возможность фильтрации по дате
    list_filter = ('pub_date',)
    # Cписок редактируемых полей, на странице списка объектов
    list_editable = ('group',)
    # Указывыем пустое значение
    empty_value_display = "-пусто-"


class GroupAdmin(admin.ModelAdmin):
    # Перечисляем поля, которые должны отображаться в админке
    list_display = ("pk", "description", "title", "slug")
    # Добавляем интерфейс для поиска по тексту групп
    search_fields = ("description", "title")
    # Указывыем пустое значение
    empty_value_display = "-пусто-"


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)

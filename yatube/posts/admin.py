from django.contrib import admin

from .models import Group, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Настройки админки для модели Post."""

    list_display = ('pk', 'text', 'pub_date', 'author', "group")
    search_fields = ('text',)
    list_filter = ('pub_date',)
    list_editable = ('group',)
    empty_value_display = "-пусто-"


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    """Настройки админки для модели Group."""

    list_display = ("pk", "description", "title", "slug")
    search_fields = ("description", "title")
    empty_value_display = "-пусто-"

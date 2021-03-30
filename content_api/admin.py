from django.contrib import admin

from .models import Category, Genre, Title


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    search_fields = ('name',)
    empty_value_display = '-пусто-'


admin.site.register(Category, CategoryAdmin)


class GenreAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    search_fields = ('name',)
    empty_value_display = '-пусто-'


admin.site.register(Genre, GenreAdmin)


class TitleAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'year', 'rating', 'category')
    search_fields = ('text',)
    list_filter = ('year', 'rating',)
    empty_value_display = '-пусто-'


admin.site.register(Title, TitleAdmin)


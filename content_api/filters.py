from django_filters import rest_framework as filters
from content_api.models import Title


class TitleFilter(filters.FilterSet):
    genre = filters.CharFilter(field_name='genre__slug', lookup_expr='exact')
    category = filters.CharFilter(field_name='category__slug',
                                  lookup_expr='exact')
    name = filters.CharFilter(lookup_expr='contains')
    year = filters.NumberFilter(lookup_expr='exact')

    class Meta:
        model = Title
        fields = ['name', 'year', 'category', 'genre']

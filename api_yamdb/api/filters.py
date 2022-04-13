import django_filters
# django_filters.CharFilter

from reviews.models import Categories, Title, Genres

class CategoryFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model = Categories
        fields = ('slug', 'titles')
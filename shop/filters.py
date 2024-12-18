import django_filters
from shop.models import Clothes, Category

class ClotheFilter(django_filters.FilterSet):
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        label='Category'
    )

    class Meta:
        model = Clothes
        fields = {
            'name': ['icontains'],
            'size': ['exact'],
            'color': ['exact'],
            'rating': ['lt', 'gt'],
            'price': ['lt', 'gt'],
            'category': ['exact'],
        }
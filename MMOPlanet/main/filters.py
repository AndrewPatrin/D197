from django_filters import FilterSet
from .models import Post

class ProductFilter(FilterSet):
    class Meta:
        model = Post
        fields = ['published_date',  'title']
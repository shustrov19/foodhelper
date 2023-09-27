from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe, Tag


class IngredientSearchFilter(SearchFilter):
    """Кастомный поисковый фильтр для ингредиентов. Замена параметра
    search на параметр name."""
    search_param = 'name'


class RecipeFilter(filters.FilterSet):
    """Кастомный фильтр для рецептов."""
    tags = filters.ModelMultipleChoiceFilter(queryset=Tag.objects.all(),
                                             field_name='tags__slug',
                                             to_field_name='slug')
    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        """Метод вывода избранных рецептов автора запроса."""
        if self.request.user.is_authenticated and value:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        """Метод вывода рецептов из списка покупок автора запроса."""
        if self.request.user.is_authenticated and value:
            return queryset.filter(shoplist__user=self.request.user)
        return queryset

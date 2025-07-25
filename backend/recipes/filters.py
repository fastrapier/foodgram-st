import django_filters
from django.db.models import Q
from .models import Recipe, Ingredient, ShoppingCart


class RecipeFilter(django_filters.FilterSet):
    """Фильтр для рецептов."""
    
    is_favorited = django_filters.NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = django_filters.NumberFilter(method='filter_is_in_shopping_cart')
    author = django_filters.NumberFilter(field_name='author__id')
    tags = django_filters.AllValuesMultipleFilter(
        field_name='tags__slug',
        lookup_expr='iexact'
    )
    
    class Meta:
        model = Recipe
        fields = ['author', 'tags']

    def filter_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorited_by__user=self.request.user)
        return queryset
    
    def filter_is_in_shopping_cart(self, queryset, name, value):
        # Проверяем, что значение параметра == 1
        if value != 1 or not self.request.user.is_authenticated:
            return queryset

        # Находим рецепты в корзине текущего пользователя
        return queryset.filter(in_shopping_carts__user=self.request.user)


class IngredientFilter(django_filters.FilterSet):
    """Фильтр для ингредиентов."""
    
    name = django_filters.CharFilter(method='filter_name')
    
    class Meta:
        model = Ingredient
        fields = ['name']
    
    def filter_name(self, queryset, name, value):
        if value:
            return queryset.filter(name__istartswith=value)
        return queryset

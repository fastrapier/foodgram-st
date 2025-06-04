import django_filters
from django.db.models import Q
from .models import Recipe, Ingredient, ShoppingCart


class RecipeFilter(django_filters.FilterSet):
    """Фильтр для рецептов."""
    
    is_favorited = django_filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = django_filters.BooleanFilter(method='filter_is_in_shopping_cart')
    author = django_filters.NumberFilter(field_name='author__id')
    tags = django_filters.AllValuesMultipleFilter(
        field_name='tags__slug',
        lookup_expr='iexact'
    )
    
    class Meta:
        model = Recipe
        fields = ['is_favorited', 'is_in_shopping_cart', 'author', 'tags']
    
    def filter_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorited_by__user=self.request.user)
        return queryset
    
    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            # Прямой запрос к модели ShoppingCart для более эффективной фильтрации
            recipes_ids = ShoppingCart.objects.filter(
                user=self.request.user
            ).values_list('recipe_id', flat=True)
            return queryset.filter(id__in=recipes_ids)
        return queryset


class IngredientFilter(django_filters.FilterSet):
    """Фильтр для ингредиентов."""
    
    name = django_filters.CharFilter(method='filter_name')
    
    class Meta:
        model = Ingredient
        fields = ['name']
    
    def filter_name(self, queryset, name, value):
        if value:
            return queryset.filter(name__icontains=value)
        return queryset

import secrets
import string

from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .filters import RecipeFilter, IngredientFilter
from .models import (
    Recipe, Ingredient, Tag, Favorite, ShoppingCart,
    ShortLink, RecipeIngredient
)
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    RecipeListSerializer, RecipeCreateUpdateSerializer,
    IngredientSerializer, TagSerializer, RecipeMinifiedSerializer, ShortLinkSerializer
)


class TagViewSet(ReadOnlyModelViewSet):
    """ViewSet для работы с тегами."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """ViewSet для работы с ингредиентами."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
    pagination_class = None

    def list(self, request, *args, **kwargs):
        """Переопределяем метод получения списка ингредиентов."""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        # Возвращаем простой список без пагинации
        return Response(serializer.data)


class RecipeViewSet(ModelViewSet):
    """ViewSet для работы с рецептами."""

    queryset = Recipe.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateUpdateSerializer
        return RecipeListSerializer

    def get_serializer_context(self):
        """
        Исключаем поле tags из ответа для соответствия схеме валидации.
        """
        context = super().get_serializer_context()
        context['exclude_tags'] = True
        return context

    def create(self, request, *args, **kwargs):
        """Создание нового рецепта."""
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            # Возвращаем более подробную информацию об ошибке для диагностики
            return Response({
                'error': str(e),
                'details': getattr(e, 'detail', str(e))
            }, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        """Выполнение создания объекта."""
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        """Добавление/удаление рецепта в избранное."""
        recipe = self.get_object()

        if request.method == 'POST':
            favorite, created = Favorite.objects.get_or_create(
                user=request.user,
                recipe=recipe
            )
            if not created:
                return Response(
                    {'errors': 'Рецепт уже добавлен в избранное'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = RecipeMinifiedSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # DELETE
        try:
            favorite = Favorite.objects.get(user=request.user, recipe=recipe)
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Favorite.DoesNotExist:
            return Response(
                {'errors': 'Рецепт не был добавлен в избранное'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        """Добавление/удаление рецепта в корзину покупок."""
        recipe = self.get_object()

        if request.method == 'POST':
            cart_item, created = ShoppingCart.objects.get_or_create(
                user=request.user,
                recipe=recipe
            )
            if not created:
                return Response(
                    {'errors': 'Рецепт уже добавлен в корзину'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = RecipeMinifiedSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # DELETE
        try:
            cart_item = ShoppingCart.objects.get(user=request.user, recipe=recipe)
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ShoppingCart.DoesNotExist:
            return Response(
                {'errors': 'Рецепт не был добавлен в корзину'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link'
    )
    def get_link(self, request, pk=None):
        """Получение короткой ссылки на рецепт."""
        recipe = self.get_object()

        short_link, created = ShortLink.objects.get_or_create(
            recipe=recipe,
            defaults={
                'short_id': self._generate_short_id()
            }
        )

        serializer = ShortLinkSerializer(short_link, context={'request': request})
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Скачивание списка покупок."""
        # Используем related_name для доступа к объектам корзины пользователя
        shopping_cart_recipes = request.user.shopping_cart.values_list('recipe', flat=True)

        if not shopping_cart_recipes:
            return Response(
                {'message': 'Корзина покупок пуста'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Собираем все ингредиенты с суммированием количества
        ingredients_dict = {}
        recipe_ingredients = RecipeIngredient.objects.filter(
            recipe__in=shopping_cart_recipes
        ).select_related('ingredient')

        for recipe_ingredient in recipe_ingredients:
            ingredient = recipe_ingredient.ingredient
            key = f"{ingredient.name} ({ingredient.measurement_unit})"

            if key in ingredients_dict:
                ingredients_dict[key] += recipe_ingredient.amount
            else:
                ingredients_dict[key] = recipe_ingredient.amount

        # Формируем текстовый файл
        shopping_list = "Список покупок:\n\n"
        for ingredient_info, amount in ingredients_dict.items():
            shopping_list += f"• {ingredient_info} — {amount}\n"

        response = HttpResponse(shopping_list, content_type='text/plain; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        return response

    def _generate_short_id(self):
        """Генерируем уникальный короткий ID."""
        length = 6
        while True:
            short_id = ''.join(
                secrets.choice(string.ascii_letters + string.digits)
                for _ in range(length)
            )
            if not ShortLink.objects.filter(short_id=short_id).exists():
                return short_id

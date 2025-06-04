from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import (
    Recipe, Ingredient, Tag, RecipeIngredient,
    Favorite, ShoppingCart, ShortLink
)
from users.models import User, Subscription
from foodgram.utils import Base64ImageField

from users.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тега."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента в рецепте."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания связи рецепт-ингредиент."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка рецептов."""

    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(source='recipe_ingredients', many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time', 'tags'
        )
        # Запрещаем дополнительные поля в ответе
        extra_kwargs = {'created': {'write_only': True}}

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Если JSON схема не ожидает поле tags, удаляем его из ответа
        if 'tags' in data and self.context.get('exclude_tags', False):
            data.pop('tags')
        return data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(
                user=request.user,
                recipe=obj
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ShoppingCart.objects.filter(
                user=request.user,
                recipe=obj
            ).exists()
        return False


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецептов."""

    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=False
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(min_value=1)

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'tags', 'name',
            'image', 'text', 'cooking_time'
        )

    def validate(self, attrs):
        # При PATCH запросе проверяем наличие ингредиентов
        if self.context['request'].method == 'PATCH' and 'ingredients' not in attrs:
            raise ValidationError({'ingredients': 'Обязательное поле.'})
        return attrs

    def validate_ingredients(self, value):
        if not value:
            raise ValidationError('Необходимо добавить хотя бы один ингредиент.')

        ingredient_ids = [item['id'] for item in value]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise ValidationError('Ингредиенты не должны повторяться.')

        # Проверяем существование ингредиентов
        existing_ingredients = Ingredient.objects.filter(id__in=ingredient_ids)
        if len(existing_ingredients) != len(ingredient_ids):
            raise ValidationError('Один или несколько ингредиентов не существуют.')

        return value

    def create_ingredients(self, recipe, ingredients_data):
        """Создаем связи рецепт-ингредиент."""
        recipe_ingredients = []
        for ingredient_data in ingredients_data:
            recipe_ingredients.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient_id=ingredient_data['id'],
                    amount=ingredient_data['amount']
                )
            )
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags', [])

        # Удаляем поле 'author' из validated_data, если оно там есть
        validated_data.pop('author', None)

        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients_data)

        # Получаем обновленный рецепт со всеми связанными данными
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)

        # Обновляем основные поля рецепта
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Обновляем теги
        if tags is not None:
            instance.tags.set(tags)

        # Обновляем ингредиенты
        if ingredients_data is not None:
            instance.recipe_ingredients.all().delete()
            self.create_ingredients(instance, ingredients_data)

        return instance

    def to_representation(self, instance):
        # Указываем, что нужно исключить поле tags из ответа
        context = self.context.copy()
        context['exclude_tags'] = True
        # Возвращаем данные в формате списка рецептов
        serializer = RecipeListSerializer(instance, context=context)
        return serializer.data


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """Сокращенный сериализатор рецепта."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserWithRecipesSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя с рецептами для подписок."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name',
            'email', 'is_subscribed', 'recipes', 'recipes_count', 'avatar'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                user=request.user,
                author=obj
            ).exists()
        return False

    def get_avatar(self, obj):
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = None
        if request:
            recipes_limit = request.query_params.get('recipes_limit')

        recipes = obj.recipes.all()
        if recipes_limit:
            try:
                recipes = recipes[:int(recipes_limit)]
            except (ValueError, TypeError):
                pass

        return RecipeMinifiedSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class ShortLinkSerializer(serializers.ModelSerializer):
    """Сериализатор короткой ссылки."""

    # Используем имя поля с дефисом, как требуется в схеме валидации
    short_link = serializers.SerializerMethodField(method_name='get_short_link')

    class Meta:
        model = ShortLink
        fields = ('short_link',)
        # Переименовываем поле в JSON-ответе
        extra_kwargs = {
            'short_link': {'source': 'short_link', 'read_only': True},
        }

    def to_representation(self, instance):
        # Переопределяем метод для замены ключа в ответе
        data = super().to_representation(instance)
        # Переименовываем ключ с подчеркиванием на ключ с дефисом
        if 'short_link' in data:
            data['short-link'] = data.pop('short_link')
        return data

    def get_short_link(self, obj):
        request = self.context.get('request')
        if request:
            domain = request.get_host()
            scheme = 'https' if request.is_secure() else 'http'
            return f"{scheme}://{domain}/s/{obj.short_id}"
        return f"/s/{obj.short_id}"

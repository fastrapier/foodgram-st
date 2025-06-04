import base64
import uuid
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import (
    Recipe, Ingredient, Tag, RecipeIngredient, 
    Favorite, ShoppingCart, Subscription, ShortLink
)
from user.models import User


class Base64ImageField(serializers.ImageField):
    """Кастомное поле для декодирования изображений из base64."""
    
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(
                base64.b64decode(imgstr), 
                name=f'recipe_{uuid.uuid4()}.{ext}'
            )
        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""
    
    is_subscribed = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 
            'last_name', 'is_subscribed', 'avatar'
        )
    
    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                user=request.user, 
                author=obj
            ).exists()
        return False


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
            'id', 'author', 'ingredients', 'tags', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )
    
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
        many=True
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(min_value=1)
    
    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'tags', 'name', 
            'image', 'text', 'cooking_time'
        )
    
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
    
    def validate_tags(self, value):
        if not value:
            raise ValidationError('Необходимо добавить хотя бы один тег.')
        
        if len(value) != len(set(value)):
            raise ValidationError('Теги не должны повторяться.')
        
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
        tags = validated_data.pop('tags')
        
        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients_data)
        
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
        # Возвращаем данные в формате списка рецептов
        serializer = RecipeListSerializer(instance, context=self.context)
        return serializer.data


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """Сокращенный сериализатор рецепта."""
    
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserWithRecipesSerializer(UserSerializer):
    """Сериализатор пользователя с рецептами для подписок."""
    
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count', 'avatar'
        )
    
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


class SetAvatarSerializer(serializers.Serializer):
    """Сериализатор для установки аватара."""
    
    avatar = Base64ImageField()
    
    def update(self, instance, validated_data):
        instance.avatar = validated_data['avatar']
        instance.save()
        return instance
    
    def to_representation(self, instance):
        return {'avatar': instance.avatar.url if instance.avatar else None}


class ShortLinkSerializer(serializers.ModelSerializer):
    """Сериализатор короткой ссылки."""
    
    short_link = serializers.SerializerMethodField()
    
    class Meta:
        model = ShortLink
        fields = ('short_link',)
    
    def get_short_link(self, obj):
        request = self.context.get('request')
        if request:
            domain = request.get_host()
            scheme = 'https' if request.is_secure() else 'http'
            return f"{scheme}://{domain}/s/{obj.short_id}"
        return f"/s/{obj.short_id}"


class SetPasswordSerializer(serializers.Serializer):
    """Сериализатор для смены пароля."""
    
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    
    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Неверный текущий пароль')
        return value
    
    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError(
                'Пароль должен содержать минимум 8 символов'
            )
        return value
    
    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user

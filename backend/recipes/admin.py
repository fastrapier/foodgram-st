from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import (
    Ingredient, Tag, Recipe, RecipeIngredient, 
    Favorite, ShoppingCart, Subscription, ShortLink
)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админ-панель для ингредиентов."""
    
    list_display = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админ-панель для тегов."""
    
    list_display = ('name', 'color', 'slug', 'colored_name')
    list_filter = ('color',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    
    def colored_name(self, obj):
        """Отображение названия тега с цветом."""
        return mark_safe(
            f'<span style="color: {obj.color}; font-weight: bold;">'
            f'{obj.name}</span>'
        )
    colored_name.short_description = 'Название с цветом'


class RecipeIngredientInline(admin.TabularInline):
    """Инлайн для ингредиентов рецепта."""
    
    model = RecipeIngredient
    extra = 1
    autocomplete_fields = ('ingredient',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админ-панель для рецептов."""
    
    list_display = (
        'name', 'author', 'cooking_time', 
        'get_tags', 'get_ingredients_count',
        'get_favorites_count', 'created'
    )
    list_filter = ('tags', 'author', 'created')
    search_fields = ('name', 'author__username', 'author__email')
    readonly_fields = ('created', 'get_image_preview')
    filter_horizontal = ('tags',)
    inlines = (RecipeIngredientInline,)
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'author', 'text', 'get_image_preview', 'image')
        }),
        ('Параметры', {
            'fields': ('cooking_time', 'tags')
        }),
        ('Системная информация', {
            'fields': ('created',),
            'classes': ('collapse',)
        })
    )
    
    def get_tags(self, obj):
        """Получение списка тегов."""
        return ', '.join([tag.name for tag in obj.tags.all()])
    get_tags.short_description = 'Теги'
    
    def get_ingredients_count(self, obj):
        """Количество ингредиентов."""
        return obj.ingredients.count()
    get_ingredients_count.short_description = 'Ингредиентов'
    
    def get_favorites_count(self, obj):
        """Количество добавлений в избранное."""
        return obj.favorites.count()
    get_favorites_count.short_description = 'В избранном'
    
    def get_image_preview(self, obj):
        """Превью изображения."""
        if obj.image:
            return mark_safe(
                f'<img src="{obj.image.url}" style="max-height: 200px; max-width: 300px;">'
            )
        return 'Нет изображения'
    get_image_preview.short_description = 'Превью изображения'


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """Админ-панель для ингредиентов рецептов."""
    
    list_display = ('recipe', 'ingredient', 'amount')
    list_filter = ('ingredient',)
    search_fields = ('recipe__name', 'ingredient__name')
    autocomplete_fields = ('recipe', 'ingredient')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админ-панель для избранного."""
    
    list_display = ('user', 'recipe', 'created')
    list_filter = ('created',)
    search_fields = ('user__username', 'recipe__name')
    autocomplete_fields = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Админ-панель для корзины покупок."""
    
    list_display = ('user', 'recipe', 'created')
    list_filter = ('created',)
    search_fields = ('user__username', 'recipe__name')
    autocomplete_fields = ('user', 'recipe')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Админ-панель для подписок."""
    
    list_display = ('user', 'author', 'created')
    list_filter = ('created',)
    search_fields = ('user__username', 'author__username')
    autocomplete_fields = ('user', 'author')


@admin.register(ShortLink)
class ShortLinkAdmin(admin.ModelAdmin):
    """Админ-панель для коротких ссылок."""
    
    list_display = ('short_id', 'recipe', 'created', 'get_full_url')
    list_filter = ('created',)
    search_fields = ('short_id', 'recipe__name')
    readonly_fields = ('short_id', 'created', 'get_full_url')
    
    def get_full_url(self, obj):
        """Полная короткая ссылка."""
        from django.conf import settings
        domain = getattr(settings, 'DOMAIN', 'localhost:8000')
        return f'http://{domain}/s/{obj.short_id}/'
    get_full_url.short_description = 'Короткая ссылка'

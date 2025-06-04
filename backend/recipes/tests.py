from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from recipes.models import Recipe, Tag, Ingredient, RecipeIngredient, Favorite, ShoppingCart
import tempfile
from PIL import Image
import base64
import io

User = get_user_model()


class RecipeModelTest(TestCase):
    """Тесты модели Recipe"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        
        self.tag = Tag.objects.create(
            name='Завтрак',
            color='#FF6600',
            slug='breakfast'
        )
        
        self.ingredient = Ingredient.objects.create(
            name='Молоко',
            measurement_unit='мл'
        )
    
    def test_recipe_creation(self):
        """Тест создания рецепта"""
        recipe = Recipe.objects.create(
            name='Тестовый рецепт',
            text='Описание рецепта',
            cooking_time=10,
            author=self.user
        )
        recipe.tags.add(self.tag)
        
        RecipeIngredient.objects.create(
            recipe=recipe,
            ingredient=self.ingredient,
            amount=200
        )
        
        self.assertEqual(recipe.name, 'Тестовый рецепт')
        self.assertEqual(recipe.author, self.user)
        self.assertEqual(recipe.tags.count(), 1)
        self.assertEqual(recipe.ingredients.count(), 1)
    
    def test_recipe_str(self):
        """Тест строкового представления рецепта"""
        recipe = Recipe.objects.create(
            name='Тестовый рецепт',
            text='Описание рецепта',
            cooking_time=10,
            author=self.user
        )
        self.assertEqual(str(recipe), 'Тестовый рецепт')


class RecipeAPITest(APITestCase):
    """Тесты API рецептов"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        self.token = Token.objects.create(user=self.user)
        
        self.tag = Tag.objects.create(
            name='Завтрак',
            color='#FF6600',
            slug='breakfast'
        )
        
        self.ingredient = Ingredient.objects.create(
            name='Молоко',
            measurement_unit='мл'
        )
        
        # Создаем тестовое изображение
        self.test_image = self.create_test_image()
    
    def create_test_image(self):
        """Создает тестовое изображение в формате base64"""
        image = Image.new('RGB', (100, 100), color='red')
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG')
        image_data = buffer.getvalue()
        return f"data:image/jpeg;base64,{base64.b64encode(image_data).decode()}"
    
    def test_recipe_list_anonymous(self):
        """Тест получения списка рецептов анонимным пользователем"""
        url = reverse('recipe-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_recipe_create_authenticated(self):
        """Тест создания рецепта авторизованным пользователем"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        data = {
            'name': 'Новый рецепт',
            'text': 'Описание нового рецепта',
            'cooking_time': 15,
            'image': self.test_image,
            'tags': [self.tag.id],
            'ingredients': [
                {
                    'id': self.ingredient.id,
                    'amount': 200
                }
            ]
        }
        
        url = reverse('recipe-list')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Recipe.objects.count(), 1)
        
        recipe = Recipe.objects.first()
        self.assertEqual(recipe.name, 'Новый рецепт')
        self.assertEqual(recipe.author, self.user)
    
    def test_recipe_create_anonymous(self):
        """Тест создания рецепта анонимным пользователем"""
        data = {
            'name': 'Новый рецепт',
            'text': 'Описание нового рецепта',
            'cooking_time': 15,
            'tags': [self.tag.id],
            'ingredients': []
        }
        
        url = reverse('recipe-list')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_add_to_favorites(self):
        """Тест добавления рецепта в избранное"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        recipe = Recipe.objects.create(
            name='Тестовый рецепт',
            text='Описание рецепта',
            cooking_time=10,
            author=self.user
        )
        
        url = reverse('recipe-favorite', kwargs={'pk': recipe.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Favorite.objects.filter(user=self.user, recipe=recipe).exists())
    
    def test_add_to_shopping_cart(self):
        """Тест добавления рецепта в список покупок"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        recipe = Recipe.objects.create(
            name='Тестовый рецепт',
            text='Описание рецепта',
            cooking_time=10,
            author=self.user
        )
        
        url = reverse('recipe-shopping-cart', kwargs={'pk': recipe.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ShoppingCart.objects.filter(user=self.user, recipe=recipe).exists())


class TagAPITest(APITestCase):
    """Тесты API тегов"""
    
    def setUp(self):
        self.tag = Tag.objects.create(
            name='Завтрак',
            color='#FF6600',
            slug='breakfast'
        )
    
    def test_tag_list(self):
        """Тест получения списка тегов"""
        url = reverse('tag-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Завтрак')


class IngredientAPITest(APITestCase):
    """Тесты API ингредиентов"""
    
    def setUp(self):
        self.ingredient = Ingredient.objects.create(
            name='Молоко',
            measurement_unit='мл'
        )
    
    def test_ingredient_list(self):
        """Тест получения списка ингредиентов"""
        url = reverse('ingredient-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Молоко')
    
    def test_ingredient_search(self):
        """Тест поиска ингредиентов"""
        url = reverse('ingredient-list')
        response = self.client.get(url, {'name': 'моло'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Поиск несуществующего ингредиента
        response = self.client.get(url, {'name': 'xyz'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

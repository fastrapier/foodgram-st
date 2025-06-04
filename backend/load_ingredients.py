import os
import sys
import django

# Настраиваем Django перед импортом моделей
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings')
django.setup()

from recipes.models import Ingredient

# Тестовые ингредиенты
test_ingredients = [
    {'name': 'Соль', 'measurement_unit': 'г'},
    {'name': 'Перец', 'measurement_unit': 'г'},
    {'name': 'Мука', 'measurement_unit': 'г'},
    {'name': 'Сахар', 'measurement_unit': 'г'},
    {'name': 'Молоко', 'measurement_unit': 'мл'},
    {'name': 'Масло растительное', 'measurement_unit': 'мл'},
    {'name': 'Яйца', 'measurement_unit': 'шт'},
    {'name': 'Картофель', 'measurement_unit': 'кг'},
    {'name': 'Лук', 'measurement_unit': 'кг'},
    {'name': 'Морковь', 'measurement_unit': 'кг'}
]

def load_ingredients():
    """Загружает тестовые ингредиенты в базу данных."""
    print("Загружаем тестовые ингредиенты...")

    # Удаляем все существующие ингредиенты
    Ingredient.objects.all().delete()

    # Создаем новые ингредиенты
    for ingr in test_ingredients:
        Ingredient.objects.create(
            name=ingr['name'],
            measurement_unit=ingr['measurement_unit']
        )

    print(f"Загружено {len(test_ingredients)} ингредиентов!")

if __name__ == '__main__':
    load_ingredients()

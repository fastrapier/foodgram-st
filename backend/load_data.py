#!/usr/bin/env python
import os
import sys
import django
import json

# Настройка Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings')
django.setup()

from recipes.models import Ingredient

def load_ingredients():
    """Загрузка ингредиентов из JSON файла."""
    file_path = '../data/ingredients.json'
    
    if not os.path.exists(file_path):
        print(f'Файл {file_path} не найден')
        return
    
    print(f'Загружаю ингредиенты из {file_path}...')
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        print(f'Найдено {len(data)} ингредиентов в файле')
        
        # Очищаем существующие ингредиенты
        existing_count = Ingredient.objects.count()
        print(f'В базе уже есть {existing_count} ингредиентов')
        
        if existing_count == 0:
            ingredients = []
            for item in data:
                ingredient = Ingredient(
                    name=item['name'],
                    measurement_unit=item['measurement_unit']
                )
                ingredients.append(ingredient)
            
            # Создаем в батчах по 1000
            batch_size = 1000
            for i in range(0, len(ingredients), batch_size):
                batch = ingredients[i:i + batch_size]
                Ingredient.objects.bulk_create(batch, ignore_conflicts=True)
                print(f'Загружено {min(i + batch_size, len(ingredients))} из {len(ingredients)} ингредиентов')
            
            print(f'Успешно загружено {len(ingredients)} ингредиентов!')
        else:
            print('Ингредиенты уже загружены')
            
        # Проверяем результат
        total_count = Ingredient.objects.count()
        print(f'Итого ингредиентов в базе: {total_count}')
        
        # Показываем первые 5 ингредиентов
        print('Первые 5 ингредиентов:')
        for ing in Ingredient.objects.all()[:5]:
            print(f'  - {ing.name} ({ing.measurement_unit})')
            
    except Exception as e:
        print(f'Ошибка при загрузке: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    load_ingredients()

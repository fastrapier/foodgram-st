#!/usr/bin/env python
import os
import sys
import django

# Настройка Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings')
django.setup()

from recipes.models import Tag

def create_default_tags():
    """Создание базовых тегов для рецептов."""
    
    default_tags = [
        {'name': 'Завтрак', 'color': '#E26C2D', 'slug': 'breakfast'},
        {'name': 'Обед', 'color': '#49B64E', 'slug': 'lunch'},
        {'name': 'Ужин', 'color': '#8775D2', 'slug': 'dinner'},
        {'name': 'Десерт', 'color': '#F93A9A', 'slug': 'dessert'},
        {'name': 'Выпечка', 'color': '#FFA500', 'slug': 'baking'},
        {'name': 'Салат', 'color': '#32CD32', 'slug': 'salad'},
    ]
    
    created_count = 0
    
    print("Создание базовых тегов...")
    
    for tag_data in default_tags:
        tag, created = Tag.objects.get_or_create(
            slug=tag_data['slug'],
            defaults={
                'name': tag_data['name'],
                'color': tag_data['color']
            }
        )
        
        if created:
            print(f"✓ Создан тег: {tag.name} ({tag.color})")
            created_count += 1
        else:
            print(f"- Тег уже существует: {tag.name}")
    
    print(f"\nСоздано новых тегов: {created_count}")
    print(f"Всего тегов в базе: {Tag.objects.count()}")
    
    # Показываем все теги
    print("\nВсе теги в базе данных:")
    for tag in Tag.objects.all():
        print(f"  {tag.name} ({tag.color}) - {tag.slug}")

if __name__ == '__main__':
    create_default_tags()

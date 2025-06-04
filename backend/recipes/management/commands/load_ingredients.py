import json
import csv
import os
from django.core.management.base import BaseCommand

from backend.recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка ингредиентов из JSON или CSV файла'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='Путь к файлу с ингредиентами (JSON или CSV)',
            default='data/ingredients.json'
        )

    def handle(self, *args, **options):
        file_path = options['file']

        if not os.path.exists(file_path):
            self.stdout.write(
                self.style.ERROR(f'Файл {file_path} не найден')
            )
            return

        if file_path.endswith('.json'):
            self.load_from_json(file_path)
        elif file_path.endswith('.csv'):
            self.load_from_csv(file_path)
        else:
            self.stdout.write(
                self.style.ERROR('Поддерживаются только JSON и CSV файлы')
            )

    def load_from_json(self, file_path):
        """Загрузка из JSON файла."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            ingredients = []
            for item in data:
                ingredient = Ingredient(
                    name=item['name'],
                    measurement_unit=item['measurement_unit']
                )
                ingredients.append(ingredient)

            Ingredient.objects.bulk_create(
                ingredients,
                ignore_conflicts=True
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Успешно загружено {len(ingredients)} ингредиентов из {file_path}'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при загрузке из JSON: {e}')
            )

    def load_from_csv(self, file_path):
        """Загрузка из CSV файла."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)

                ingredients = []
                for row in reader:
                    ingredient = Ingredient(
                        name=row['name'],
                        measurement_unit=row['measurement_unit']
                    )
                    ingredients.append(ingredient)

                Ingredient.objects.bulk_create(
                    ingredients,
                    ignore_conflicts=True
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Успешно загружено {len(ingredients)} ингредиентов из {file_path}'
                    )
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при загрузке из CSV: {e}')
            )

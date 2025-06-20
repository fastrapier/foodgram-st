import csv
import json
import os

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """Команда для импорта ингредиентов из CSV или JSON файла."""

    help = 'Импорт ингредиентов из файла в БД'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv',
            action='store_true',
            help='Импорт из csv файла (по умолчанию)',
        )
        parser.add_argument(
            '--json',
            action='store_true',
            help='Импорт из json файла',
        )
        parser.add_argument(
            '--path',
            type=str,
            help='Путь к файлу с данными (по умолчанию: data/ingredients.csv или data/ingredients.json)',
        )

    def handle(self, *args, **options):
        # Определяем путь к файлу
        path = options.get('path')
        use_json = options.get('json')

        self.stdout.write(self.style.SUCCESS(f'Начало импорта ингредиентов. JSON: {use_json}, путь: {path}'))

        if not path:
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'data')
            if use_json:
                path = os.path.join(data_dir, 'ingredients.json')
            else:
                path = os.path.join(data_dir, 'ingredients.csv')

            self.stdout.write(self.style.SUCCESS(f'Автоопределение пути к файлу: {path}'))
            self.stdout.write(self.style.SUCCESS(f'Директория существует: {os.path.exists(os.path.dirname(path))}'))
            self.stdout.write(self.style.SUCCESS(f'Полный путь к data: {os.path.abspath(data_dir)}'))

        # Проверяем существование файла
        if not os.path.exists(path):
            self.stdout.write(self.style.ERROR(f'Файл {path} не найден!'))
            self.stdout.write(self.style.ERROR(f'Текущая директория: {os.getcwd()}'))
            return

        # Загружаем ингредиенты
        ingredients_count = 0

        if use_json:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    self.stdout.write(self.style.SUCCESS(f'Чтение JSON файла...'))
                    ingredients_data = json.load(f)
                    self.stdout.write(self.style.SUCCESS(f'Найдено {len(ingredients_data)} ингредиентов в JSON'))

                    for item in ingredients_data:
                        try:
                            obj, created = Ingredient.objects.get_or_create(
                                name=item['name'],
                                measurement_unit=item['measurement_unit']
                            )
                            if created:
                                ingredients_count += 1
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f'Ошибка при создании ингредиента {item["name"]}: {e}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Ошибка при обработке JSON файла: {e}'))
                return
        else:  # CSV по умолчанию
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    self.stdout.write(self.style.SUCCESS(f'Чтение CSV файла...'))
                    reader = csv.reader(f)
                    # Пропускаем заголовок, если он есть
                    try:
                        header = next(reader)
                        if header and len(header) >= 2:
                            # Проверяем, содержит ли заголовок ожидаемые поля
                            if 'name' in header[0].lower() or 'measurement_unit' in header[1].lower():
                                self.stdout.write('Пропускаем заголовок файла')
                            else:
                                # Если это не заголовок, а данные, возвращаемся в начало
                                f.seek(0)
                    except StopIteration:
                        self.stdout.write(self.style.ERROR('Файл пуст!'))
                        return

                    for row in reader:
                        if len(row) < 2:
                            self.stdout.write(self.style.WARNING(f'Пропущена строка: {row} - недостаточно данных'))
                            continue

                        name, measurement_unit = row[0], row[1]
                        try:
                            obj, created = Ingredient.objects.get_or_create(
                                name=name,
                                measurement_unit=measurement_unit
                            )
                            if created:
                                ingredients_count += 1
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f'Ошибка при создании ингредиента {name}: {e}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Ошибка при обработке CSV файла: {e}'))
                return

        self.stdout.write(self.style.SUCCESS(f'Успешно импортировано {ingredients_count} ингредиентов!'))

        # Проверяем итоговое количество ингредиентов в базе
        total_count = Ingredient.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Всего ингредиентов в базе: {total_count}'))

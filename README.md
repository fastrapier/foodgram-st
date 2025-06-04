# Foodgram - Сервис для обмена рецептами

## 📋 Описание проекта

Foodgram - это веб-приложение для публикации и обмена рецептами. Пользователи могут создавать свои рецепты, добавлять рецепты в избранное, подписываться на авторов и формировать список покупок на основе выбранных рецептов.

## 🚀 Технологии

**Backend:**
- Python 3.12+
- Django 5.2.1
- Django REST Framework 3.16.0
- PostgreSQL / SQLite
- Djoser (аутентификация)
- Pillow (обработка изображений)
- django-filter (фильтрация)
- django-cors-headers (CORS)

**Frontend:**
- React.js
- Bootstrap

**Инфраструктура:**
- Docker & Docker Compose
- Nginx

## 🛠 Установка и запуск

### Локальная разработка

1. **Клонирование репозитория:**
```bash
git clone <repository-url>
cd foodgram-st
```

2. **Установка зависимостей:**
```bash
pip install -r requirements.txt
# Для разработки:
pip install -r requirements-dev.txt
```

3. **Настройка базы данных:**
```bash
cd backend
python manage.py migrate
python manage.py createsuperuser
```

4. **Загрузка тестовых данных:**
```bash
# Загрузка ингредиентов
python manage.py load_ingredients

# Создание тегов (опционально)
python create_tags.py
```

5. **Запуск сервера разработки:**
```bash
python manage.py runserver
```

API будет доступно по адресу: http://localhost:8000/api/

### Docker (Продакшен)

Находясь в папке infra, выполните команду:
```bash
docker-compose up
```

При выполнении этой команды контейнер frontend подготовит файлы для фронтенд-приложения.

- Фронтенд: http://localhost
- API документация: http://localhost/api/docs/

## 📚 API Документация

### Основные эндпоинты:

**Пользователи:**
- `GET/POST /api/users/` - список пользователей / регистрация
- `GET /api/users/{id}/` - профиль пользователя
- `GET /api/users/me/` - текущий пользователь
- `PUT/DELETE /api/users/me/avatar/` - управление аватаром
- `POST /api/users/set_password/` - смена пароля
- `POST/DELETE /api/users/{id}/subscribe/` - подписка/отписка
- `GET /api/users/subscriptions/` - мои подписки

**Рецепты:**
- `GET/POST /api/recipes/` - список рецептов / создание
- `GET/PUT/PATCH/DELETE /api/recipes/{id}/` - операции с рецептом
- `POST/DELETE /api/recipes/{id}/favorite/` - избранное
- `POST/DELETE /api/recipes/{id}/shopping_cart/` - список покупок
- `GET /api/recipes/{id}/get_link/` - короткая ссылка
- `GET /api/recipes/download_shopping_cart/` - скачать список покупок

**Ингредиенты:**
- `GET /api/ingredients/` - список ингредиентов (с поиском)
- `GET /api/ingredients/{id}/` - ингредиент

**Теги:**
- `GET /api/tags/` - список тегов
- `GET /api/tags/{id}/` - тег

**Авторизация:**
- `POST /api/auth/token/login/` - получить токен
- `POST /api/auth/token/logout/` - удалить токен

## 🔧 Конфигурация

### Переменные окружения:

```bash
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@localhost:5432/foodgram
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com
```

### Настройки CORS:

В `settings.py` настроены CORS для локальной разработки. Для продакшена укажите нужные домены в `CORS_ALLOWED_ORIGINS`.

## 📁 Структура проекта

```
foodgram-st/
├── backend/           # Django API
│   ├── foodgram/     # Настройки проекта
│   ├── recipes/      # Приложение рецептов
│   ├── user/         # Приложение пользователей
│   └── manage.py
├── frontend/         # React приложение
├── infra/           # Docker конфигурация
├── data/            # Данные для загрузки
└── docs/            # API документация
```

## 🧪 Тестирование

```bash
cd backend
python manage.py test
```

## 📝 Особенности реализации

1. **Изображения**: Поддержка загрузки изображений в формате Base64
2. **Фильтрация**: Рецепты можно фильтровать по автору, тегам, избранному
3. **Поиск**: Поиск ингредиентов по названию
4. **Короткие ссылки**: Генерация коротких ссылок на рецепты
5. **Список покупок**: Автоматическое суммирование ингредиентов
6. **Подписки**: Система подписок на авторов рецептов

## 👥 Авторы

- Backend API: Django REST Framework
- Frontend: React.js

## 📄 Лицензия

MIT License


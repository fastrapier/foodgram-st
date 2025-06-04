FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Добавляем права на выполнение скрипта
RUN chmod +x entrypoint.sh

# Используем entrypoint.sh вместо прямого запуска gunicorn
CMD ["./entrypoint.sh"]

# Используем Python образ
FROM python:3.10-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем содержимое вашего проекта в контейнер
COPY . /app

# Устанавливаем зависимости (если есть файл requirements.txt)
RUN pip install --no-cache-dir -r requirements.txt

# Открываем порт 5000 для приложения Flask
EXPOSE 5000

# Команда для запуска Flask-приложения
CMD ["flask", "run", "--host=0.0.0.0"]

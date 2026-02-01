# Базовый образ — slim для минимального размера
FROM python:3.12-slim

# Не кэшируем stdout/stderr — логи сразу видны в docker logs
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Копируем requirements первым — слой кэшируется если зависимости не менялись
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальной код
COPY . .

# Создаём папку data если не существует
RUN mkdir -p data

# Запускаем бот
CMD ["python", "main.py"]

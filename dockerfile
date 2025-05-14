# Используем минимальный образ Python
FROM python:3.12-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY . .

# (опционально) Устанавливаем зависимости, если они есть
# Если у тебя есть requirements.txt — раскомментируй следующую строку:
RUN pip install --no-cache-dir -r requirements.txt

# Или укажи вручную нужные зависимости, например:
# RUN pip install aiohttp

# Запускаем сервер
CMD ["python", "server.py"]

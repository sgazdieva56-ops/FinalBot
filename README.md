# Mood Tracker Bot

Telegram бот для отслеживания настроения и продуктивности.

## Возможности

- Отслеживание настроения
- Учет сна
- Учет работы/учебы
- Графики
- Инсайты
- История
- PostgreSQL

## Установка

```bash
git clone <repo>
cd mood-bot
```

## Установка зависимостей

```bash
pip install -r requirements.txt
```

## PostgreSQL

Создать базу:

```sql
CREATE DATABASE mood_bot;
```

Применить схему:

```bash
psql -U postgres -d mood_bot -f schema.sql
```

Тестовые данные:

```bash
psql -U postgres -d mood_bot -f test_data.sql
```

## .env

```env
BOT_TOKEN=YOUR_TOKEN
DB_NAME=mood_bot
DB_USER=postgres
DB_PASSWORD=123
DB_HOST=localhost
DB_PORT=5432
```

## Запуск

```bash
python bot.py
```
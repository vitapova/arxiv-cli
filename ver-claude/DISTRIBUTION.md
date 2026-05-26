# Распространение arXiv Assistant

## Для кого эта система?

✅ AGI исследователи  
✅ PhD студенты  
✅ Учёные любых областей  
✅ Все кто работает с научными статьями

---

## 🚀 Три способа использования

### 1. 📱 Публичный Telegram Bot (САМЫЙ ПРОСТОЙ)

**Для пользователей:**
1. Открыть Telegram
2. Найти бота `@arxiv_assistant_bot` (когда создашь)
3. Нажать /start
4. Готово!

**Для тебя (один раз):**
1. Создать бота через @BotFather
2. Запустить на сервере: `python3 bot/standalone_bot.py`
3. Бот доступен всем

**Плюсы:**
- ✅ Пользователям НЕ нужно ничего устанавливать
- ✅ Работает на любом устройстве (телефон, планшет)
- ✅ Push уведомления

**Минусы:**
- ❌ Нужен сервер (или твой Mac постоянно включён)
- ❌ Одна библиотека на всех (или нужна multiuser версия)

---

### 2. 🖥️ Локальная установка (CLI + Web UI)

**Для пользователей:**

```bash
# 1. Клонировать
git clone https://github.com/vitapova/arxiv-cli
cd arxiv-cli/ver-claude

# 2. Установить
pip install -e .

# 3. Использовать
python3 -m arxiv_cli.cli --help  # CLI
python3 web/app.py               # Web UI на localhost
```

**Плюсы:**
- ✅ Полный контроль
- ✅ Работает без интернета
- ✅ Своя приватная библиотека
- ✅ Web UI + CLI

**Минусы:**
- ❌ Нужны технические навыки
- ❌ Установка Python/git

---

### 3. 🦞 OpenClaw Skill (для продвинутых)

**Для пользователей OpenClaw:**

```bash
# Установка через OpenClaw
openclaw skill install arxiv-assistant

# Использование через чат
"Найди статьи про quantum computing"
"Добавь статью 1706.03762 в библиотеку"
"Настрой дайджест каждый день в 9:00"
```

**Плюсы:**
- ✅ Интеграция с личным AI ассистентом
- ✅ Scheduled задачи
- ✅ Контекстное понимание

**Минусы:**
- ❌ Только для пользователей OpenClaw

---

## 📊 Сравнение подходов

| Параметр | Публичный бот | Локальная установка | OpenClaw Skill |
|----------|:-------------:|:-------------------:|:--------------:|
| **Простота для пользователя** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **Не нужна установка** | ✅ | ❌ | ❌ |
| **Приватность данных** | ⚠️ | ✅ | ✅ |
| **Работает без интернета** | ❌ | ✅ | ⚠️ |
| **Push уведомления** | ✅ | ❌ | ✅ |
| **Кастомизация** | ❌ | ✅ | ✅ |
| **Multiuser** | ✅ | ❌ | ❌ |

---

## 🎯 Рекомендация для массового использования

### Фаза 1: MVP (сейчас)
**Публичный Telegram бот** на сервере
- Простой для пользователей
- Быстрый старт
- feedback

### Фаза 2: Scaling (если популярно)
**Multiuser версия:**
- База данных (PostgreSQL) вместо JSON
- User authentication
- Cloud hosting (Heroku/Railway/DigitalOcean)

### Фаза 3: Advanced (для power users)
- **OpenClaw Skill** для тех у кого есть OpenClaw
- **Docker image** для лёгкой установки
- **Web app** (не localhost, а публичный сайт)

---

## 📝 Инструкция для исследователей

### Вариант A: Используй готового бота (когда запущу)

1. Открой Telegram
2. Найди `@arxivita_bot`
3. /start
4. Готово!

### Вариант B: Установи локально (для приватности)

**Требования:**
- Python 3.8+
- Git

**Шаги:**
```bash
# Клонировать
git clone https://github.com/vitapova/arxiv-cli
cd arxiv-cli/ver-claude

# Установить
pip install -e .

# CLI использование
python3 -m arxiv_cli.cli search "quantum computing"
python3 -m arxiv_cli.cli library

# Web UI (опционально)
pip install fastapi uvicorn jinja2
python3 web/app.py
# Открыть http://localhost:5002

# Telegram бот (опционально)
pip install python-telegram-bot
export TELEGRAM_BOT_TOKEN='ваш_токен'
python3 bot/standalone_bot.py
```

### Вариант C: Через OpenClaw (если установлен)

```bash
openclaw skill install arxiv-assistant from https://github.com/vitapova/arxiv-cli
```


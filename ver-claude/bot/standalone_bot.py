#!/usr/bin/env python3
"""
Standalone Telegram Bot для arXiv Assistant

Работает независимо от OpenClaw.
Каждый пользователь имеет свою библиотеку.
"""

import os
import sys
import logging
from pathlib import Path

# Добавляем путь к arxiv_cli
sys.path.insert(0, str(Path(__file__).parent.parent))

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

from bot.telegram_bot import handle_command

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start."""
    response = handle_command('start')
    
    # Формируем inline клавиатуру
    keyboard = []
    if 'buttons' in response:
        for row in response['buttons']:
            keyboard.append([
                InlineKeyboardButton(btn['text'], callback_data=btn['callback'])
                for btn in row
            ])
    
    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    
    await update.message.reply_text(
        response['text'],
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def library_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /library."""
    response = handle_command('library')
    
    keyboard = []
    if 'buttons' in response:
        for row in response['buttons']:
            keyboard.append([
                InlineKeyboardButton(btn['text'], callback_data=btn['callback'])
                for btn in row
            ])
    
    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    
    await update.message.reply_text(
        response['text'],
        reply_markup=reply_markup,
        parse_mode='Markdown',
        disable_web_page_preview=True
    )


async def search_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /search."""
    query = ' '.join(context.args) if context.args else ''
    response = handle_command('search', query)
    
    keyboard = []
    if 'buttons' in response:
        for row in response['buttons']:
            keyboard.append([
                InlineKeyboardButton(btn['text'], callback_data=btn['callback'])
                for btn in row
            ])
    
    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    
    await update.message.reply_text(
        response['text'],
        reply_markup=reply_markup,
        parse_mode='Markdown',
        disable_web_page_preview=True
    )


async def add_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /add."""
    arxiv_id = context.args[0] if context.args else ''
    response = handle_command('add', arxiv_id)
    
    keyboard = []
    if 'buttons' in response:
        for row in response['buttons']:
            keyboard.append([
                InlineKeyboardButton(btn['text'], callback_data=btn['callback'])
                for btn in row
            ])
    
    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    
    await update.message.reply_text(
        response['text'],
        reply_markup=reply_markup,
        parse_mode='Markdown',
        disable_web_page_preview=True
    )


async def info_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /info."""
    arxiv_id = context.args[0] if context.args else ''
    response = handle_command('info', arxiv_id)
    
    keyboard = []
    if 'buttons' in response:
        for row in response['buttons']:
            keyboard.append([
                InlineKeyboardButton(btn['text'], callback_data=btn['callback'])
                for btn in row
            ])
    
    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    
    await update.message.reply_text(
        response['text'],
        reply_markup=reply_markup,
        parse_mode='Markdown',
        disable_web_page_preview=True
    )


async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /stats."""
    response = handle_command('stats')
    
    await update.message.reply_text(
        response['text'],
        parse_mode='Markdown'
    )


async def digest_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /digest."""
    period = context.args[0] if context.args else 'week'
    response = handle_command('digest', period)
    
    await update.message.reply_text(
        response['text'],
        parse_mode='Markdown',
        disable_web_page_preview=True
    )


async def authors_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /authors."""
    response = handle_command('authors')
    
    keyboard = []
    if 'buttons' in response:
        for row in response['buttons']:
            keyboard.append([
                InlineKeyboardButton(btn['text'], callback_data=btn['callback'])
                for btn in row
            ])
    
    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    
    await update.message.reply_text(
        response['text'],
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help."""
    response = handle_command('help')
    
    await update.message.reply_text(
        response['text'],
        parse_mode='Markdown'
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий на inline кнопки."""
    query = update.callback_query
    await query.answer()
    
    # Парсим callback_data
    data = query.data
    
    if data.startswith('/'):
        parts = data.split(maxsplit=1)
        cmd = parts[0][1:]
        args = parts[1] if len(parts) > 1 else ''
        
        response = handle_command(cmd, args)
        
        # Формируем новую клавиатуру если есть
        keyboard = []
        if 'buttons' in response:
            for row in response['buttons']:
                keyboard.append([
                    InlineKeyboardButton(btn['text'], callback_data=btn['callback'])
                    for btn in row
                ])
        
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        
        await query.edit_message_text(
            text=response['text'],
            reply_markup=reply_markup,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )


def main():
    """Запуск бота."""
    # Получаем токен из переменной окружения
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("❌ Ошибка: не указан TELEGRAM_BOT_TOKEN")
        print("\nУстановите переменную окружения:")
        print("  export TELEGRAM_BOT_TOKEN='your_token_here'")
        print("\nИли создайте файл .env:")
        print("  TELEGRAM_BOT_TOKEN=your_token_here")
        sys.exit(1)
    
    # Создаём приложение
    application = Application.builder().token(token).build()
    
    # Регистрируем команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("library", library_cmd))
    application.add_handler(CommandHandler("search", search_cmd))
    application.add_handler(CommandHandler("add", add_cmd))
    application.add_handler(CommandHandler("info", info_cmd))
    application.add_handler(CommandHandler("stats", stats_cmd))
    application.add_handler(CommandHandler("digest", digest_cmd))
    application.add_handler(CommandHandler("authors", authors_cmd))
    application.add_handler(CommandHandler("help", help_cmd))
    
    # Обработка inline кнопок
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Запуск
    print("🤖 arXiv Assistant Bot запущен!")
    print("⌨️  Press Ctrl+C to stop")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()

"""
Управление конфигурацией

Хранение настроек CLI:
- сохранённые запросы для watch
- предпочтения вывода
- пути для загрузок

Файл конфигурации: ~/.arxiv-cli/config.json
"""

import json
import os
from pathlib import Path


CONFIG_DIR = Path.home() / '.arxiv-cli'
CONFIG_FILE = CONFIG_DIR / 'config.json'


def load_config():
    """
    Загрузка конфигурации.
    
    Returns:
        dict: настройки
    """
    # TODO: реализация
    pass


def save_config(config):
    """
    Сохранение конфигурации.
    
    Args:
        config: dict с настройками
    """
    # TODO: реализация
    pass


def get_watches():
    """Получить список сохранённых запросов."""
    # TODO: реализация
    pass


def add_watch(name, query):
    """Добавить запрос для отслеживания."""
    # TODO: реализация
    pass


def remove_watch(name):
    """Удалить запрос."""
    # TODO: реализация
    pass

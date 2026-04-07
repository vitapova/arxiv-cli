"""
Интеграционные тесты CLI
"""

import pytest
import tempfile
import os
from pathlib import Path
from click.testing import CliRunner
from arxiv_cli.cli import cli


@pytest.fixture
def runner():
    """CLI runner."""
    return CliRunner()


@pytest.fixture(autouse=True)
def temp_files(monkeypatch):
    """Использовать временные файлы."""
    with tempfile.TemporaryDirectory() as tmpdir:
        lib_file = Path(tmpdir) / 'library.json'
        sub_file = Path(tmpdir) / 'subscriptions.json'
        monkeypatch.setattr('arxiv_cli.utils.library.LIBRARY_FILE', lib_file)
        monkeypatch.setattr('arxiv_cli.utils.subscriptions.SUBSCRIPTIONS_FILE', sub_file)
        yield tmpdir


class TestCLISearch:
    """Тесты команды search через CLI."""
    
    def test_search_basic(self, runner):
        """Базовый поиск."""
        result = runner.invoke(cli, ['search', 'quantum', '--max', '2'])
        
        assert result.exit_code == 0
        assert 'Поиск' in result.output
        assert 'Найдено результатов' in result.output
    
    def test_search_with_category(self, runner):
        """Поиск с категорией."""
        result = runner.invoke(cli, ['search', 'transformer', '--category', 'cs.CL', '--max', '1'])
        
        assert result.exit_code == 0
    
    def test_search_compact(self, runner):
        """Поиск в компактном формате."""
        result = runner.invoke(cli, ['search', 'GPT', '--max', '1', '--compact'])
        
        assert result.exit_code == 0
        assert 'ID:' in result.output
    
    def test_search_table(self, runner):
        """Поиск в табличном формате."""
        result = runner.invoke(cli, ['search', 'quantum', '--max', '2', '--table'])
        
        assert result.exit_code == 0
        assert '№' in result.output or 'ID' in result.output


class TestCLIDownload:
    """Тесты команды download через CLI."""
    
    def test_download_simple(self, runner, temp_files):
        """Простое скачивание."""
        output = os.path.join(temp_files, 'test.pdf')
        result = runner.invoke(cli, ['download', '1706.03762', '--output', output, '--no-library'])
        
        assert result.exit_code == 0
        assert 'Успешно скачано' in result.output
        assert os.path.exists(output)
    
    def test_download_auto_name(self, runner, temp_files):
        """Скачивание с автоименованием."""
        result = runner.invoke(cli, ['download', '1706.03762', '--output-dir', temp_files, '--auto-name', '--no-library'])
        
        assert result.exit_code == 0
        assert 'Vaswani' in result.output or '2017' in result.output


class TestCLIAdd:
    """Тесты команды add через CLI."""
    
    def test_add_to_library(self, runner):
        """Добавление в библиотеку."""
        result = runner.invoke(cli, ['add', '1706.03762', '--tag', 'test'])
        
        assert result.exit_code == 0
        assert 'Добавлено в библиотеку' in result.output
        assert 'Attention Is All You Need' in result.output


class TestCLIList:
    """Тесты команды list через CLI."""
    
    def test_list_empty(self, runner):
        """Список пустой библиотеки."""
        result = runner.invoke(cli, ['list'])
        
        assert result.exit_code == 0
        assert 'Библиотека пуста' in result.output or 'Библиотека:' in result.output
    
    def test_list_with_entries(self, runner):
        """Список с записями."""
        # Сначала добавляем
        runner.invoke(cli, ['add', '1706.03762'])
        
        # Затем смотрим список
        result = runner.invoke(cli, ['list'])
        
        assert result.exit_code == 0
        assert 'Библиотека:' in result.output
    
    def test_list_table(self, runner):
        """Список в табличном формате."""
        runner.invoke(cli, ['add', '1706.03762'])
        
        result = runner.invoke(cli, ['list', '--table'])
        
        assert result.exit_code == 0
        assert 'ID' in result.output
    
    def test_list_mark_read(self, runner):
        """Отметка как прочитанная."""
        runner.invoke(cli, ['add', '1706.03762'])
        
        result = runner.invoke(cli, ['list', '--mark-read', '1706.03762v7'])
        
        assert result.exit_code == 0
        assert 'отмечена как прочитанная' in result.output


class TestCLIInfo:
    """Тесты команды info через CLI."""
    
    def test_info_from_api(self, runner):
        """Информация из API."""
        result = runner.invoke(cli, ['info', '1706.03762'])
        
        assert result.exit_code == 0
        assert 'Attention Is All You Need' in result.output
        assert 'Vaswani' in result.output
    
    def test_info_from_library(self, runner):
        """Информация из библиотеки."""
        runner.invoke(cli, ['add', '1706.03762', '--tag', 'test'])
        
        result = runner.invoke(cli, ['info', '1706.03762v7', '--library'])
        
        assert result.exit_code == 0
        assert 'Библиотека' in result.output
        assert 'test' in result.output


class TestCLIExport:
    """Тесты команды export через CLI."""
    
    def test_export_stats(self, runner):
        """Статистика экспорта."""
        runner.invoke(cli, ['add', '1706.03762'])
        
        result = runner.invoke(cli, ['export', '--stats'])
        
        assert result.exit_code == 0
        assert 'Статей в библиотеке' in result.output
    
    def test_export_single_bibtex(self, runner):
        """Экспорт одной статьи в BibTeX."""
        result = runner.invoke(cli, ['export', '1706.03762', '--format', 'bibtex'])
        
        assert result.exit_code == 0
        assert '@article{' in result.output
        assert 'Vaswani' in result.output


class TestCLITrack:
    """Тесты команд track через CLI."""
    
    def test_track_add(self, runner):
        """Добавление в отслеживание."""
        result = runner.invoke(cli, ['track', 'add', '1706.03762'])
        
        assert result.exit_code == 0
        assert 'Добавлено в отслеживание' in result.output
    
    def test_track_list(self, runner):
        """Список отслеживаемых."""
        runner.invoke(cli, ['track', 'add', '1706.03762'])
        
        result = runner.invoke(cli, ['track', 'list'])
        
        assert result.exit_code == 0
        assert 'Отслеживаемых статей' in result.output
    
    def test_track_versions(self, runner):
        """История версий."""
        runner.invoke(cli, ['track', 'add', '1706.03762'])
        
        result = runner.invoke(cli, ['track', 'versions', '1706.03762'])
        
        assert result.exit_code == 0
        assert 'История версий' in result.output


class TestCLISubscribe:
    """Тесты команд subscribe через CLI."""
    
    def test_subscribe_add(self, runner):
        """Создание подписки."""
        result = runner.invoke(cli, ['subscribe', 'add', '--query', 'quantum computing', '--name', 'Test'])
        
        assert result.exit_code == 0
        assert 'Подписка создана' in result.output
    
    def test_subscribe_list(self, runner):
        """Список подписок."""
        runner.invoke(cli, ['subscribe', 'add', '--query', 'test'])
        
        result = runner.invoke(cli, ['subscribe', 'list'])
        
        assert result.exit_code == 0
        assert 'Подписок' in result.output


class TestCLIDigest:
    """Тесты команды digest через CLI."""
    
    def test_digest_help(self, runner):
        """Справка по digest."""
        result = runner.invoke(cli, ['digest', '--help'])
        
        assert result.exit_code == 0
        assert 'period' in result.output

"""
Тесты для команд CLI
"""

import pytest
import tempfile
import os
from arxiv_cli.commands.search import search_articles, build_search_query
from arxiv_cli.commands.download import download_pdf, generate_filename
from arxiv_cli.commands.export import export_single, export_library
from arxiv_cli.utils.library import add_entry, get_entries, load_library, LIBRARY_FILE


class TestSearchCommand:
    """Тесты для команды search."""
    
    def test_build_search_query_simple(self):
        """Тест построения простого запроса."""
        query = build_search_query('quantum computing')
        assert 'all:quantum computing' in query
    
    def test_build_search_query_with_category(self):
        """Тест запроса с категорией."""
        query = build_search_query('', categories=['cs.AI'])
        assert 'cat:cs.AI' in query
    
    def test_build_search_query_with_multiple_categories(self):
        """Тест запроса с несколькими категориями."""
        query = build_search_query('', categories=['cs.AI', 'cs.LG'])
        assert 'cat:cs.AI' in query
        assert 'cat:cs.LG' in query
        assert 'OR' in query
    
    def test_build_search_query_with_author(self):
        """Тест запроса с автором."""
        query = build_search_query('', authors=['Vaswani'])
        assert 'au:Vaswani' in query
    
    def test_build_search_query_with_dates(self):
        """Тест запроса с датами."""
        query = build_search_query('quantum', date_from='2020-01-01', date_to='2020-12-31')
        assert 'submittedDate:' in query
        assert '20200101' in query
        assert '20201231' in query
    
    def test_search_articles_real(self):
        """Тест реального поиска."""
        results = search_articles('quantum', max_results=3)
        
        assert 'entries' in results
        assert 'total_results' in results
        assert len(results['entries']) <= 3
        assert results['total_results'] > 0


class TestDownloadCommand:
    """Тесты для команды download."""
    
    def test_generate_filename(self):
        """Тест генерации имени файла."""
        entry = {
            'id': '1706.03762',
            'authors': ['Ashish Vaswani', 'Noam Shazeer'],
            'published': '2017-06-12'
        }
        
        filename = generate_filename('1706.03762', entry)
        assert '1706.03762' in filename
        assert 'Vaswani' in filename
        assert '2017' in filename
        assert filename.endswith('.pdf')
    
    def test_generate_filename_no_authors(self):
        """Тест генерации имени без авторов."""
        entry = {
            'id': '1234.5678',
            'authors': [],
            'published': '2020-01-01'
        }
        
        filename = generate_filename('1234.5678', entry)
        assert '1234.5678' in filename
        assert 'unknown' in filename
    
    def test_generate_filename_with_version(self):
        """Тест генерации имени с версией."""
        entry = {
            'id': '1706.03762v7',
            'authors': ['Ashish Vaswani'],
            'published': '2017-06-12'
        }
        
        filename = generate_filename('1706.03762v7', entry)
        assert '1706.03762v7' in filename or '1706.03762-v7' in filename
    
    def test_download_pdf_real(self):
        """Тест реального скачивания PDF."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'test.pdf')
            
            # Скачиваем известную статью
            file_path, entry = download_pdf(
                '1706.03762',
                output_path=output_path,
                save_to_library=False
            )
            
            # Проверяем файл
            assert os.path.exists(file_path)
            assert os.path.getsize(file_path) > 0
            
            # Проверяем метаданные
            assert entry['title']
            assert len(entry['authors']) > 0
    
    def test_download_with_auto_name(self):
        """Тест скачивания с автоименованием."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path, entry = download_pdf(
                '1706.03762',
                output_dir=tmpdir,
                auto_name=True,
                save_to_library=False
            )
            
            # Проверяем что файл создан с правильным именем
            assert os.path.exists(file_path)
            basename = os.path.basename(file_path)
            assert '1706.03762' in basename
            assert 'Vaswani' in basename or '2017' in basename
    
    def test_download_batch(self):
        """Тест пакетного скачивания."""
        from arxiv_cli.commands.download import download_batch
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Создаём batch-файл
            batch_file = os.path.join(tmpdir, 'batch.txt')
            with open(batch_file, 'w') as f:
                f.write('# Test batch\n')
                f.write('1706.03762\n')
                f.write('2301.07041\n')
            
            # Скачиваем
            results = download_batch(
                batch_file,
                output_dir=tmpdir,
                save_to_library=False
            )
            
            # Проверяем результаты
            assert len(results) == 2
            assert all(r[2] == 'success' for r in results)
            
            # Проверяем файлы
            for arxiv_id, file_path, status, entry in results:
                assert os.path.exists(file_path)
                assert os.path.getsize(file_path) > 0
    
    def test_download_batch_with_errors(self):
        """Тест пакетного скачивания с ошибками."""
        from arxiv_cli.commands.download import download_batch
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Создаём batch с несуществующей статьёй
            batch_file = os.path.join(tmpdir, 'batch.txt')
            with open(batch_file, 'w') as f:
                f.write('1706.03762\n')
                f.write('9999.99999\n')  # Несуществующая
            
            results = download_batch(batch_file, output_dir=tmpdir, save_to_library=False)
            
            assert len(results) == 2
            
            # Первая успешна
            assert results[0][2] == 'success'
            
            # Вторая с ошибкой
            assert results[1][2] == 'error'
    
    def test_download_batch_empty_file(self):
        """Тест пакетного скачивания пустого файла."""
        from arxiv_cli.commands.download import download_batch
        from arxiv_cli.api.client import ArxivAPIError
        
        with tempfile.TemporaryDirectory() as tmpdir:
            batch_file = os.path.join(tmpdir, 'empty.txt')
            with open(batch_file, 'w') as f:
                f.write('# Only comments\n')
                f.write('# Nothing to download\n')
            
            with pytest.raises(ArxivAPIError):
                download_batch(batch_file, output_dir=tmpdir)
    
    def test_download_batch_missing_file(self):
        """Тест пакетного скачивания несуществующего файла."""
        from arxiv_cli.commands.download import download_batch
        from arxiv_cli.api.client import ArxivAPIError
        
        with pytest.raises(ArxivAPIError):
            download_batch('/tmp/nonexistent_file.txt')


class TestExportCommand:
    """Тесты для команды export."""
    
    def test_export_single_bibtex(self):
        """Тест экспорта одной статьи в BibTeX."""
        result = export_single('1706.03762', format='bibtex')
        
        assert '@article{' in result
        assert 'title = {' in result
        assert 'author = {' in result
        assert 'Attention Is All You Need' in result
        assert 'Vaswani' in result
    
    def test_export_single_csl(self):
        """Тест экспорта одной статьи в CSL JSON."""
        import json
        
        result = export_single('1706.03762', format='csl')
        data = json.loads(result)
        
        assert data['id']
        assert data['type'] == 'article-journal'
        assert 'title' in data
        assert 'author' in data
        assert len(data['author']) > 0
    
    def test_export_library_bibtex(self):
        """Тест экспорта библиотеки в BibTeX."""
        from arxiv_cli.commands.export import export_library
        from arxiv_cli.utils.library import add_entry
        
        # Добавляем статьи в библиотеку
        entry1 = {
            'id': '1111.1111',
            'title': 'Test Paper 1',
            'authors': ['Author 1'],
            'categories': ['cs.AI'],
            'published': '2020-01-01',
            'updated': '2020-01-01',
            'abstract': 'Test',
            'primary_category': 'cs.AI',
            'pdf_url': 'https://example.com',
            'abs_url': 'https://example.com'
        }
        
        entry2 = {
            'id': '2222.2222',
            'title': 'Test Paper 2',
            'authors': ['Author 2'],
            'categories': ['cs.CL'],
            'published': '2020-02-01',
            'updated': '2020-02-01',
            'abstract': 'Test',
            'primary_category': 'cs.CL',
            'pdf_url': 'https://example.com',
            'abs_url': 'https://example.com'
        }
        
        add_entry(entry1, tags=['ai'])
        add_entry(entry2, tags=['nlp'])
        
        # Экспортируем всё
        result = export_library(format='bibtex')
        
        assert '@article{' in result
        assert 'Test Paper 1' in result
        assert 'Test Paper 2' in result
    
    def test_export_library_csl(self):
        """Тест экспорта библиотеки в CSL."""
        import json
        from arxiv_cli.commands.export import export_library
        from arxiv_cli.utils.library import add_entry, load_library
        
        entry = {
            'id': '3333.3333',
            'title': 'Test Paper CSL Export',
            'authors': ['Test Author'],
            'categories': ['cs.AI'],
            'published': '2020-01-01',
            'updated': '2020-01-01',
            'abstract': 'Test',
            'primary_category': 'cs.AI',
            'pdf_url': 'https://example.com',
            'abs_url': 'https://example.com'
        }
        
        add_entry(entry)
        
        result = export_library(format='csl')
        data = json.loads(result)
        
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Находим нашу статью
        our_paper = [p for p in data if 'CSL Export' in p.get('title', '')]
        assert len(our_paper) == 1
        assert our_paper[0]['title'] == 'Test Paper CSL Export'
    
    def test_export_library_with_filter(self):
        """Тест экспорта с фильтром."""
        from arxiv_cli.commands.export import export_library
        from arxiv_cli.utils.library import add_entry
        
        entry1 = {
            'id': '4444.4444',
            'title': 'AI Paper',
            'authors': ['Author'],
            'categories': ['cs.AI'],
            'published': '2020-01-01',
            'updated': '2020-01-01',
            'abstract': 'Test',
            'primary_category': 'cs.AI',
            'pdf_url': 'https://example.com',
            'abs_url': 'https://example.com'
        }
        
        entry2 = {
            'id': '5555.5555',
            'title': 'NLP Paper',
            'authors': ['Author'],
            'categories': ['cs.CL'],
            'published': '2020-01-01',
            'updated': '2020-01-01',
            'abstract': 'Test',
            'primary_category': 'cs.CL',
            'pdf_url': 'https://example.com',
            'abs_url': 'https://example.com'
        }
        
        add_entry(entry1, tags=['ai'])
        add_entry(entry2, tags=['nlp'])
        
        # Экспорт с фильтром по тегу
        result = export_library(format='bibtex', tags=['ai'])
        
        assert 'AI Paper' in result
        assert 'NLP Paper' not in result


class TestLibrary:
    """Тесты для библиотеки статей."""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Сохранение и восстановление библиотеки."""
        # Бэкап текущей библиотеки
        backup = None
        if LIBRARY_FILE.exists():
            backup = LIBRARY_FILE.read_text()
            LIBRARY_FILE.unlink()
        
        yield
        
        # Восстановление
        if backup:
            LIBRARY_FILE.write_text(backup)
        elif LIBRARY_FILE.exists():
            LIBRARY_FILE.unlink()
    
    def test_add_entry(self):
        """Тест добавления статьи в библиотеку."""
        entry = {
            'id': '1234.5678',
            'title': 'Test Paper',
            'authors': ['Test Author'],
            'categories': ['cs.AI']
        }
        
        add_entry(entry, tags=['test'])
        
        library = load_library()
        assert len(library['entries']) == 1
        assert library['entries'][0]['id'] == '1234.5678'
        assert 'test' in library['entries'][0]['tags']
    
    def test_get_entries_with_filter(self):
        """Тест фильтрации статей."""
        # Добавляем несколько статей
        entry1 = {
            'id': '1234.5678',
            'title': 'Test Paper 1',
            'authors': ['Author 1'],
            'categories': ['cs.AI']
        }
        entry2 = {
            'id': '2345.6789',
            'title': 'Test Paper 2',
            'authors': ['Author 2'],
            'categories': ['cs.CL']
        }
        
        add_entry(entry1, tags=['ai'])
        add_entry(entry2, tags=['nlp'])
        
        # Фильтр по категории
        entries = get_entries(category='cs.AI')
        assert len(entries) == 1
        assert entries[0]['id'] == '1234.5678'
        
        # Фильтр по тегу
        entries = get_entries(tags=['nlp'])
        assert len(entries) == 1
        assert entries[0]['id'] == '2345.6789'

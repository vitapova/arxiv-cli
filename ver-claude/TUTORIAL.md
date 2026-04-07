# Руководство для начинающих: как пользоваться arXiv CLI

*Пошаговая инструкция для тех, кто не знаком с командной строкой*

## Что такое командная строка?

Командная строка (терминал, консоль) — это способ управления компьютером с помощью текстовых команд. Вместо кликов мышкой вы печатаете команды.

**Как открыть терминал:**
- **macOS:** Spotlight (Cmd+Space) → введите "Terminal" → Enter
- **Windows:** Win+R → введите "cmd" → Enter
- **Linux:** Ctrl+Alt+T

## Шаг 1: Установка

### 1.1 Проверьте Python

Откройте терминал и введите:

```bash
python3 --version
```

Вы должны увидеть что-то вроде: `Python 3.9.6` или выше.

Если Python не установлен:
- **macOS:** `brew install python3` (нужен Homebrew)
- **Windows:** Скачайте с https://www.python.org/downloads/
- **Linux:** `sudo apt install python3` (Ubuntu/Debian)

### 1.2 Скачайте проект

```bash
# Перейдите в удобную папку (например, Документы)
cd ~/Documents

# Скачайте проект
git clone https://github.com/vitapova/arxiv-cli
cd arxiv-cli/ver-claude

# Установите утилиту
pip3 install -e .
```

**Что это значит:**
- `cd` — Change Directory (перейти в папку)
- `git clone` — скачать проект с GitHub
- `pip3 install -e .` — установить программу

## Шаг 2: Первые команды

### 2.1 Поиск статьи

Допустим, вы хотите найти статьи про "transformer":

```bash
python3 -m arxiv_cli.cli search "transformer" --max 3
```

**Что это делает:**
- `python3 -m arxiv_cli.cli` — запускает программу
- `search` — команда поиска
- `"transformer"` — что ищем
- `--max 3` — показать 3 результата

**Результат:** Вы увидите список статей с названиями, авторами и ссылками.

### 2.2 Скачать статью

Предположим, вам понравилась статья с ID `1706.03762`:

```bash
python3 -m arxiv_cli.cli download 1706.03762
```

**Результат:** Файл `1706.03762.pdf` появится в текущей папке.

**Скачать с красивым именем:**

```bash
python3 -m arxiv_cli.cli download 1706.03762 --auto-name
```

**Результат:** Файл будет называться `1706.03762_Vaswani_2017.pdf`

### 2.3 Посмотреть информацию

Хотите узнать больше о статье перед скачиванием?

```bash
python3 -m arxiv_cli.cli info 1706.03762
```

**Результат:** Полная информация: авторы, аннотация, ссылки.

## Шаг 3: Работа с библиотекой

### 3.1 Добавить статью в библиотеку

Сохраните статью в свою личную библиотеку (без скачивания PDF):

```bash
python3 -m arxiv_cli.cli add 1706.03762 --tag transformers --tag nlp
```

**Результат:** Статья добавлена в библиотеку с тегами "transformers" и "nlp".

### 3.2 Посмотреть библиотеку

```bash
python3 -m arxiv_cli.cli list
```

**Результат:** Список всех ваших статей с тегами и статусами.

**Табличный формат (компактнее):**

```bash
python3 -m arxiv_cli.cli list --table
```

### 3.3 Фильтры

**Показать только непрочитанные:**
```bash
python3 -m arxiv_cli.cli list --status unread
```

**Показать статьи с тегом "gpt":**
```bash
python3 -m arxiv_cli.cli list --tag gpt
```

**Поиск по названию:**
```bash
python3 -m arxiv_cli.cli list --search "attention"
```

### 3.4 Отметить как прочитанную

```bash
python3 -m arxiv_cli.cli list --mark-read 1706.03762
```

**Добавить в избранное:**

```bash
python3 -m arxiv_cli.cli list --star 1706.03762
```

## Шаг 4: Экспорт для работы

### 4.1 Экспорт в BibTeX (для LaTeX)

```bash
python3 -m arxiv_cli.cli export --all --format bibtex -o my_papers.bib
```

**Результат:** Файл `my_papers.bib` со всеми вашими статьями. Используйте его в LaTeX:

```latex
\bibliography{my_papers}
\cite{Vaswani2017_1706_03762}
```

### 4.2 Экспорт только статей с тегом

```bash
python3 -m arxiv_cli.cli export --tag gpt --format bibtex -o gpt_papers.bib
```

## Шаг 5: Дайджесты

### 5.1 Что нового за неделю?

```bash
python3 -m arxiv_cli.cli digest --period week --query "LLM" --max 10
```

**Результат:** Список новых статей про LLM за последнюю неделю, сгруппированных по категориям.

### 5.2 Экспорт дайджеста

```bash
python3 -m arxiv_cli.cli digest --period month --category cs.AI --format markdown --export digest.md
```

**Результат:** Красиво оформленный Markdown-файл с дайджестом.

## Шаг 6: Подписки

### 6.1 Создать подписку

Хотите отслеживать новые статьи по теме?

```bash
python3 -m arxiv_cli.cli subscribe add --query "quantum computing" --category cs.AI --name "Quantum"
```

### 6.2 Проверить обновления

```bash
python3 -m arxiv_cli.cli subscribe check
```

**Результат:** Показывает ТОЛЬКО новые статьи, которых не было при прошлой проверке.

### 6.3 Список подписок

```bash
python3 -m arxiv_cli.cli subscribe list
```

## Шаг 7: Отслеживание версий

### 7.1 Добавить в отслеживание

Препринты обновляются. Отследите статью:

```bash
python3 -m arxiv_cli.cli track add 1706.03762
```

### 7.2 Проверить обновления

```bash
python3 -m arxiv_cli.cli track update
```

**Результат:** Если вышла новая версия статьи (v2, v3...), вы узнаете об этом.

### 7.3 История версий

```bash
python3 -m arxiv_cli.cli track versions 1706.03762
```

## Полезные советы

### Справка по любой команде

Забыли параметры? Добавьте `--help`:

```bash
python3 -m arxiv_cli.cli search --help
python3 -m arxiv_cli.cli download --help
```

### Куда сохраняются файлы?

- **PDF:** В текущую папку (где вы запустили команду)
- **Библиотека:** `~/.arxiv-cli/library.json`
- **Подписки:** `~/.arxiv-cli/subscriptions.json`

**Где `~`?**
- macOS/Linux: `/Users/ваше_имя/` (домашняя папка)
- Windows: `C:\Users\ваше_имя\`

### Как указать путь для PDF?

**Полный путь:**
```bash
python3 -m arxiv_cli.cli download 1706.03762 -o ~/Downloads/paper.pdf
```

**Папка:**
```bash
python3 -m arxiv_cli.cli download 1706.03762 -d ~/Documents/papers
```

### Пакетное скачивание

Создайте файл `ids.txt`:
```
1706.03762
2005.14165
2301.07041
```

Скачайте все:
```bash
python3 -m arxiv_cli.cli download --batch ids.txt --output-dir papers --auto-name
```

## Типичные ошибки

### "command not found: python3"
**Решение:** Установите Python (см. Шаг 1.1)

### "No such file or directory"
**Решение:** Проверьте, что вы в правильной папке. Используйте `pwd` (Unix) или `cd` (Windows) чтобы узнать где вы.

### "Rate limit" или 429 ошибка
**Решение:** Программа автоматически подождёт и повторит. Если не помогло — подождите 1-2 минуты.

### "Статья не найдена"
**Решение:** Проверьте правильность arXiv ID. Формат: `1234.56789` или `1234.56789v2`

## Быстрый старт: типичный сценарий

```bash
# 1. Найти статьи
python3 -m arxiv_cli.cli search "quantum machine learning" --max 5 --table

# 2. Добавить интересные в библиотеку
python3 -m arxiv_cli.cli add 2301.12345 --tag quantum --tag ml

# 3. Скачать PDF нужных статей
python3 -m arxiv_cli.cli download 2301.12345 --auto-name

# 4. Посмотреть библиотеку
python3 -m arxiv_cli.cli list --table

# 5. Экспортировать для работы
python3 -m arxiv_cli.cli export --all --format bibtex -o papers.bib
```

## Дополнительная помощь

- **Полная документация:** [README.md](README.md)
- **Примеры команд:** В README есть примеры для каждой команды
- **Проблемы:** Опишите ошибку и что вы делали — это поможет найти решение

---

**Удачи в работе с arXiv! 🚀**

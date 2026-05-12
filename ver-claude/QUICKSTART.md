# 🚀 Быстрый старт arXiv CLI

## Где код?

**GitHub:** https://github.com/vitapova/arxiv-cli

**На твоём Mac:**  
`/Users/vitapotapova/.openclaw/workspace/arxiv-cli/ver-claude/`

---

## Как запустить (3 простых шага)

### 1️⃣ Открой Terminal

**Через Finder:**
1. Открой **Finder** (улыбающаяся иконка в Dock)
2. Слева кликни **Applications** (Программы)
3. Найди папку **Utilities** (Утилиты)  
4. Двойной клик на **Terminal**

### 2️⃣ Перейди в папку проекта

Скопируй эту команду и вставь в Terminal (Cmd+V), нажми Enter:

```bash
cd /Users/vitapotapova/.openclaw/workspace/arxiv-cli/ver-claude
```

### 3️⃣ Готово! Теперь можешь использовать команды

---

## 🎨 Красивые команды (с цветами!)

Все команды ниже добавь `--rich` для цветного вывода.

### Посмотреть библиотеку

```bash
python3 -m arxiv_cli.cli list --rich
```

**Увидишь:** Красивую таблицу со статьями, иконками статуса, тегами.

### Статистика

```bash
python3 -m arxiv_cli.cli export --stats --rich
```

**Увидишь:** Панель с количеством статей, таблицу категорий, облако тегов.

### Информация о статье

```bash
python3 -m arxiv_cli.cli info 2103.00020v1 --library --rich
```

**Увидишь:** Красивую карточку со всеми деталями.

### Фильтры

```bash
# Только прочитанные
python3 -m arxiv_cli.cli list --status read --rich

# По тегу
python3 -m arxiv_cli.cli list --tag gpt --rich

# Поиск
python3 -m arxiv_cli.cli list --search "attention" --rich
```

---

## 📝 Без интернета (100% работают)

```bash
# Таблица библиотеки
python3 -m arxiv_cli.cli list --rich

# Экспорт в BibTeX
python3 -m arxiv_cli.cli export --all --format bibtex

# Добавить теги
python3 -m arxiv_cli.cli info 2103.00020v1 --add-tag machine-learning

# Отметить прочитанной
python3 -m arxiv_cli.cli list --mark-read 2005.14165v4

# Добавить в избранное
python3 -m arxiv_cli.cli list --star 1706.03762v7

# Статистика
python3 -m arxiv_cli.cli export --stats --rich
```

---

## 🌐 С интернетом (когда сеть работает)

```bash
# Поиск (с цветами - пока не реализовано, но скоро!)
python3 -m arxiv_cli.cli search "quantum" --max 5 --table

# Скачать PDF
python3 -m arxiv_cli.cli download 1706.03762 --auto-name

# Добавить в библиотеку
python3 -m arxiv_cli.cli add 2301.07041 --tag crypto
```

---

## 💡 Подсказки

**Справка по любой команде:**
```bash
python3 -m arxiv_cli.cli list --help
```

**Сохранить результат в файл:**
```bash
python3 -m arxiv_cli.cli export --all --format bibtex -o ~/Downloads/papers.bib
```

**Скопировать команду:** Выдели → Cmd+C  
**Вставить в Terminal:** Cmd+V

---

## ⚠️ Если не работает

**"command not found"**  
Убедись что ты в правильной папке:
```bash
pwd
# Должно показать: /Users/vitapotapova/.openclaw/workspace/arxiv-cli/ver-claude
```

**"Rate limit"**  
Подожди 10-30 минут, arXiv разблокирует. Или используй команды без интернета (list, export, info).

**Другая ошибка**  
Скопируй текст ошибки и покажи мне.

---

## 📱 Еще проще

Запомни эту одну команду для быстрого доступа:

```bash
alias arxiv='cd /Users/vitapotapova/.openclaw/workspace/arxiv-cli/ver-claude && python3 -m arxiv_cli.cli'
```

После этого можно просто:
```bash
arxiv list --rich
arxiv info 1706.03762v7 --library --rich
```

(Алиас работает только в текущей сессии Terminal. Для постоянного добавь в `~/.zshrc`)

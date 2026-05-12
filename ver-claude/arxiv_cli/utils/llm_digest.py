"""
LLM-enhanced digest

Использование LLM для улучшения дайджестов
"""

import os


def rank_papers_by_importance(papers, field='AGI', model='gpt-4'):
    """
    Ранжирование статей по важности для области.
    
    Args:
        papers: список статей
        field: область исследований (AGI, ML, CV, etc.)
        model: модель для использования
        
    Returns:
        list: отранжированные статьи с оценками
    """
    # Формируем промпт
    papers_text = ""
    for i, paper in enumerate(papers, 1):
        authors = ', '.join(paper['authors'][:3])
        if len(paper['authors']) > 3:
            authors += ' et al.'
        
        papers_text += f"""
{i}. Title: {paper['title']}
   Authors: {authors}
   Categories: {', '.join(paper['categories'])}
   Abstract: {paper['abstract'][:300]}...
   ID: {paper['id']}

"""
    
    prompt = f"""You are an expert {field} researcher. Rank these papers by importance for {field} research.

Papers:
{papers_text}

Return ONLY a JSON array of paper IDs in order of importance (most important first):
["id1", "id2", "id3", ...]

Consider:
- Novelty of approach
- Potential impact on {field}
- Quality of work
- Relevance to current trends
"""
    
    # Вызов LLM (нужно настроить API)
    try:
        import openai
        
        client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        
        response = client.chat.completions.create(
            model=model,
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.3
        )
        
        import json
        ranked_ids = json.loads(response.choices[0].message.content)
        
        # Переупорядочиваем papers
        id_to_paper = {p['id']: p for p in papers}
        ranked_papers = []
        
        for paper_id in ranked_ids:
            if paper_id in id_to_paper:
                paper = id_to_paper[paper_id]
                paper['importance_rank'] = len(ranked_papers) + 1
                ranked_papers.append(paper)
        
        # Добавляем не попавшие в ранжирование
        for paper in papers:
            if paper['id'] not in ranked_ids:
                ranked_papers.append(paper)
        
        return ranked_papers
    
    except Exception as e:
        # Если LLM недоступен — возвращаем как есть
        return papers


def generate_narrative_digest(papers, period='week', field='AGI'):
    """
    Генерация связного повествовательного дайджеста.
    
    Args:
        papers: список статей
        period: период (day/week/month)
        field: область исследований
        
    Returns:
        str: markdown текст дайджеста
    """
    # Топ-5 статей
    papers_text = ""
    for i, paper in enumerate(papers[:10], 1):
        authors = ', '.join(paper['authors'][:3])
        if len(paper['authors']) > 3:
            authors += ' et al.'
        
        papers_text += f"""
**{i}. {paper['title']}**
Authors: {authors}
Categories: {', '.join(paper['categories'])}
Abstract: {paper['abstract'][:400]}...
arXiv: {paper['id']}

---

"""
    
    period_names = {'day': 'день', 'week': 'неделю', 'month': 'месяц'}
    
    prompt = f"""You are an {field} research newsletter writer. Create an engaging weekly digest.

Based on these recent papers, write a narrative digest that includes:
1. Key trends and themes (2-3 paragraphs)
2. Breakthrough papers (highlight 3-5 most important)
3. Connections between works
4. Implications for {field} research

Recent papers from the past {period_names.get(period, 'week')}:

{papers_text}

Write in Russian. Use Markdown. Be insightful and concise.
Target audience: {field} researchers.
"""
    
    try:
        import openai
        
        client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        
        response = client.chat.completions.create(
            model='gpt-4',
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        # Fallback — обычный дайджест
        from arxiv_cli.utils.formatter import format_digest
        
        digest_data = {
            'period': period,
            'date_from': '',
            'date_to': '',
            'total': len(papers),
            'entries': papers,
            'grouped': {},
            'statistics': {'total': len(papers), 'by_category': {}}
        }
        
        return format_digest(digest_data, format='markdown')


def summarize_paper(paper, style='brief'):
    """
    LLM суммаризация одной статьи.
    
    Args:
        paper: данные статьи
        style: стиль (brief, detailed, eli5, technical)
        
    Returns:
        str: summary
    """
    styles = {
        'brief': 'Summarize in 2-3 sentences',
        'detailed': 'Summarize key methodology, results, and conclusions',
        'eli5': 'Explain like I\'m 5 (simple language)',
        'technical': 'Technical summary for experts with mathematical details'
    }
    
    instruction = styles.get(style, styles['brief'])
    
    prompt = f"""{instruction}:

Title: {paper['title']}
Authors: {', '.join(paper['authors'][:5])}
Abstract: {paper['abstract']}

Language: Russian
"""
    
    try:
        import openai
        
        client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        
        response = client.chat.completions.create(
            model='gpt-4o-mini',  # Cheaper model для summaries
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.3
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        # Fallback — первые N символов аннотации
        return paper['abstract'][:300] + '...'

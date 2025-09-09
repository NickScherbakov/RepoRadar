import requests
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime, timedelta
import os

# Настройки
REPORADAR_URL = os.getenv('REPORADAR_URL', 'https://your-reporadar-app.herokuapp.com')
CHARTS_DIR = 'charts'

def get_stats():
    """Получить статистику из RepoRadar."""
    try:
        response = requests.get(f'{REPORADAR_URL}/stats', timeout=10)
        response.raise_for_status()
        return response.json()['data']
    except Exception as e:
        print(f"Error getting stats: {e}")
        return None

def get_transfers():
    """Получить данные о переносах."""
    try:
        response = requests.get(f'{REPORADAR_URL}/export', timeout=10)
        response.raise_for_status()
        return response.json()['data']
    except Exception as e:
        print(f"Error getting transfers: {e}")
        return []

def generate_overview_chart(stats):
    """Генерировать общий обзор."""
    if not stats:
        return

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle('RepoRadar Dashboard - Обзор рынка репозиториев', fontsize=16)

    # Общая статистика
    labels = ['Всего переносов', 'Уникальных покупателей', 'Уникальных продавцов']
    values = [stats.get('total_transfers', 0), stats.get('unique_buyers', 0), stats.get('unique_sellers', 0)]
    ax1.bar(labels, values, color=['#1f77b4', '#ff7f0e', '#2ca02c'])
    ax1.set_title('Общая статистика')
    ax1.tick_params(axis='x', rotation=45)

    # Топ покупателей
    if 'top_buyers' in stats and stats['top_buyers']:
        buyers = stats['top_buyers'][:10]
        names = [b['new_owner'][:15] + '...' if len(b['new_owner']) > 15 else b['new_owner'] for b in buyers]
        counts = [b['count'] for b in buyers]
        ax2.barh(names[::-1], counts[::-1], color='#1f77b4')
        ax2.set_title('Топ 10 покупателей')

    # Распределение по звездам
    transfers = get_transfers()
    if transfers:
        stars = [t.get('stars', 0) for t in transfers if t.get('stars', 0) > 0]
        if stars:
            ax3.hist(stars, bins=20, color='#ff7f0e', alpha=0.7)
            ax3.set_title('Распределение по звездам')
            ax3.set_xlabel('Количество звезд')
            ax3.set_ylabel('Количество репозиториев')

    # Динамика (если есть данные по времени)
    if transfers:
        dates = []
        for t in transfers:
            if 'created_at' in t:
                try:
                    date = datetime.fromisoformat(t['created_at'].replace('Z', '+00:00'))
                    dates.append(date.date())
                except:
                    pass

        if dates:
            date_counts = pd.Series(dates).value_counts().sort_index()
            ax4.plot(date_counts.index[-30:], date_counts.values[-30:], color='#2ca02c')
            ax4.set_title('Динамика переносов (последние 30 дней)')
            ax4.tick_params(axis='x', rotation=45)

    plt.tight_layout()
    os.makedirs(CHARTS_DIR, exist_ok=True)
    plt.savefig(f'{CHARTS_DIR}/overview.png', dpi=150, bbox_inches='tight')
    plt.close()

def generate_language_chart():
    """Генерировать график по языкам программирования."""
    transfers = get_transfers()
    if not transfers:
        return

    languages = {}
    for t in transfers:
        lang = t.get('language', 'Unknown')
        if lang:
            languages[lang] = languages.get(lang, 0) + 1

    if languages:
        top_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:10]
        langs, counts = zip(*top_langs)

        plt.figure(figsize=(10, 6))
        plt.bar(langs, counts, color='#9467bd')
        plt.title('Популярные языки в перенесенных репозиториях')
        plt.xticks(rotation=45, ha='right')
        plt.ylabel('Количество репозиториев')
        plt.tight_layout()
        plt.savefig(f'{CHARTS_DIR}/languages.png', dpi=150, bbox_inches='tight')
        plt.close()

def update_readme():
    """Обновить README.md с актуальными данными."""
    stats = get_stats()
    if not stats:
        return

    readme_content = f"""# NickScherbakov

## 📊 RepoRadar Dashboard

Мониторинг рынка репозиториев GitHub - отслеживание покупок и продаж репозиториев.

### 📈 Общая статистика
- **Всего переносов**: {stats.get('total_transfers', 0)}
- **Уникальных покупателей**: {stats.get('unique_buyers', 0)}
- **Уникальных продавцов**: {stats.get('unique_sellers', 0)}

### 📊 Визуализация
![Обзор рынка](charts/overview.png)

### 🏷️ Популярные языки
![Языки программирования](charts/languages.png)

### 🔄 Последние переносы
| Репозиторий | Старый владелец | Новый владелец | Звезды | Дата |
|-------------|----------------|----------------|--------|------|
"""

    transfers = get_transfers()[:10]  # Последние 10
    for t in transfers:
        repo = t.get('repo', 'N/A')
        old_owner = t.get('old_owner', 'N/A')
        new_owner = t.get('new_owner', 'N/A')
        stars = t.get('stars', 0)
        date = t.get('created_at', 'N/A')[:10] if t.get('created_at') else 'N/A'
        readme_content += f"| {repo} | {old_owner} | {new_owner} | {stars} | {date} |\n"

    readme_content += f"\n*Dashboard обновляется автоматически. Последнее обновление: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}*"

    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)

if __name__ == '__main__':
    print("Генерация графиков...")
    stats = get_stats()
    if stats:
        generate_overview_chart(stats)
        generate_language_chart()
        update_readme()
        print("Готово!")
    else:
        print("Не удалось получить данные из RepoRadar")
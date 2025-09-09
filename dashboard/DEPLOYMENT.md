# Инструкции по развертыванию RepoRadar Dashboard

## Шаг 1: Создание репозитория для dashboard

1. Создайте новый репозиторий на GitHub с именем `{ваш_username}/{ваш_username}`
   - Например: `NickScherbakov/NickScherbakov`
   - Это специальный репозиторий, который GitHub использует для профиля

2. Скопируйте все файлы из папки `dashboard/` в новый репозиторий:

   ```bash
   # В папке dashboard текущего репозитория
   git init
   git add .
   git commit -m "Initial dashboard setup"
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_USERNAME.git
   git push -u origin main
   ```

## Шаг 2: Развертывание RepoRadar

### Вариант 1: Railway (Рекомендуется)

```bash
# Установите Railway CLI
npm install -g @railway/cli

# Авторизуйтесь
railway login

# Создайте проект
railway init

# Свяжите с текущим репозиторием
railway link

# Разверните
railway up
```

### Вариант 2: Heroku

```bash
# Установите Heroku CLI
# Создайте приложение
heroku create your-reporadar-app

# Настройте переменные окружения
heroku config:set GITHUB_TOKEN=your_github_token
heroku config:set DATABASE_PATH=/app/data/reporadar.db

# Разверните
git push heroku main
```

### Вариант 3: DigitalOcean App Platform

1. Создайте приложение через веб-интерфейс DigitalOcean
2. Подключите репозиторий
3. Настройте переменные окружения
4. Разверните

## Шаг 3: Настройка секретов в dashboard репозитории

1. Перейдите в Settings > Secrets and variables > Actions
2. Добавьте секрет `REPORADAR_URL` со значением URL вашего развернутого RepoRadar
   - Например: `https://your-reporadar-app.up.railway.app`

## Шаг 4: Тестирование

1. Запустите workflow вручную в dashboard репозитории
2. Проверьте, что графики генерируются в папке `charts/`
3. Убедитесь, что README.md обновляется с актуальными данными

## Шаг 5: Настройка мониторинга

### Добавление данных для тестирования

```python
# В app.py добавьте тестовые данные
@app.route('/test-data')
def add_test_data():
    test_transfers = [
        {
            'repo': 'test/repo1',
            'old_owner': 'olduser',
            'new_owner': 'google',
            'date': datetime.now().isoformat(),
            'stars': 1500,
            'language': 'Python'
        },
        # Добавьте больше тестовых данных...
    ]

    for transfer in test_transfers:
        db.add_transfer(**transfer)

    return jsonify({'status': 'Test data added'})
```

### Проверка работоспособности

- Посетите `https://your-reporadar-app.com/health` для проверки здоровья
- Посетите `https://your-reporadar-app.com/stats` для проверки статистики
- Посетите `https://your-reporadar-app.com/export` для проверки экспорта

## Переменные окружения для RepoRadar

```bash
# Обязательные
GITHUB_TOKEN=your_github_personal_access_token

# Опциональные
PORT=5000
DEBUG=false
DATABASE_PATH=reporadar.db
```

## Структура файлов dashboard репозитория

```text
YOUR_USERNAME/
├── .github/
│   └── workflows/
│       └── update-dashboard.yml
├── charts/
│   └── .gitkeep
├── generate_charts.py
├── requirements.txt
└── README.md
```

## Устранение неполадок

### Проблема: Графики не генерируются

**Решение**: Проверьте, что `REPORADAR_URL` секрет настроен правильно и RepoRadar доступен

### Проблема: Workflow не запускается

**Решение**: Проверьте логи GitHub Actions и убедитесь, что все зависимости установлены

### Проблема: README не обновляется

**Решение**: Проверьте права на запись в репозиторий для GitHub Actions

## Следующие шаги

1. Настройте мониторинг большего количества репозиториев в `config.yaml`
2. Добавьте больше графиков (например, по времени, по компаниям)
3. Настройте уведомления о важных переносах
4. Добавьте интерактивные элементы с Plotly

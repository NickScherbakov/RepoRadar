# RepoRadar Deployment Guide

## 🚀 Быстрое развертывание на Railway

### Шаг 1: Подготовка
1. Создайте аккаунт на [Railway.app](https://railway.app)
2. Установите Railway CLI: `npm install -g @railway/cli`
3. Авторизуйтесь: `railway login`

### Шаг 2: Развертывание
```bash
# В корне проекта RepoRadar
railway login
railway init
railway up
```

### Шаг 3: Настройка переменных окружения
```bash
# Установите GitHub токен
railway variables set GITHUB_TOKEN=your_github_personal_access_token

# Опционально: другие настройки
railway variables set DEBUG=false
railway variables set DATABASE_PATH=/app/data/reporadar.db
```

### Шаг 4: Получение URL
```bash
railway domain
# Это даст вам URL типа: https://reporadar-production.up.railway.app
```

## 🔧 Альтернативные платформы

### Heroku
```bash
# Установите Heroku CLI
heroku create your-reporadar-app
heroku config:set GITHUB_TOKEN=your_github_token
git push heroku main
```

### DigitalOcean App Platform
1. Создайте приложение через веб-интерфейс
2. Подключите этот репозиторий
3. Настройте переменные окружения
4. Разверните

## 📋 Необходимые переменные окружения

```bash
GITHUB_TOKEN=your_github_personal_access_token  # Обязательно
DEBUG=false                                     # Опционально
DATABASE_PATH=/app/data/reporadar.db           # Опционально
PORT=5000                                       # Опционально
```

## ✅ Проверка развертывания

После развертывания проверьте:
- `https://your-app-url/health` - статус здоровья
- `https://your-app-url/stats` - статистика
- `https://your-app-url/export` - экспорт данных

## 🎯 Следующие шаги

1. **Получите URL** развернутого приложения
2. **Создайте dashboard репозиторий** `YOUR_USERNAME/YOUR_USERNAME`
3. **Скопируйте файлы** из папки `dashboard/`
4. **Настройте секрет** `REPORADAR_URL` в dashboard репозитории
5. **Запустите workflow** для генерации графиков
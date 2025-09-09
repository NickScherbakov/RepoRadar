#!/bin/bash

echo "🚀 Начинаем развертывание RepoRadar на Railway"
echo ""

# Проверка наличия Railway CLI
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI не найден. Установите его:"
    echo "npm install -g @railway/cli"
    exit 1
fi

# Проверка авторизации
echo "🔐 Проверяем авторизацию в Railway..."
if ! railway whoami &> /dev/null; then
    echo "❌ Вы не авторизованы в Railway. Выполните:"
    echo "railway login"
    exit 1
fi

echo "✅ Авторизация подтверждена"

# Инициализация проекта
echo ""
echo "📦 Инициализируем проект..."
railway init --name reporadar --source . --language python

# Развертывание
echo ""
echo "🚀 Развертываем приложение..."
railway up

# Получение URL
echo ""
echo "🌐 Получаем URL приложения..."
sleep 5
railway domain

echo ""
echo "✅ Развертывание завершено!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Скопируйте URL из вывода выше"
echo "2. Перейдите в Railway dashboard для настройки переменных окружения"
echo "3. Установите GITHUB_TOKEN"
echo "4. Создайте dashboard репозиторий"
echo ""
echo "🔗 Railway Dashboard: https://railway.app/dashboard"
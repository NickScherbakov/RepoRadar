#!/bin/bash

echo "🎯 Создание RepoRadar Dashboard репозитория"
echo ""

# Проверка наличия GitHub CLI
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI не найден. Установите его:"
    echo "https://cli.github.com/"
    exit 1
fi

# Проверка авторизации
if ! gh auth status &> /dev/null; then
    echo "❌ Вы не авторизованы в GitHub CLI. Выполните:"
    echo "gh auth login"
    exit 1
fi

echo "✅ GitHub CLI готов"

# Создание репозитория
echo ""
echo "📦 Создаем репозиторий NickScherbakov/NickScherbakov..."
gh repo create NickScherbakov --public --description "📊 RepoRadar Dashboard - GitHub Repository Market Analytics"

# Клонирование репозитория
echo ""
echo "📥 Клонируем репозиторий..."
git clone https://github.com/NickScherbakov/NickScherbakov.git dashboard-repo
cd dashboard-repo

# Копирование файлов
echo ""
echo "📋 Копируем dashboard файлы..."
cp -r ../dashboard/* ./

# Настройка git
echo ""
echo "🔧 Настраиваем git..."
git add .
git commit -m "🎯 Initial RepoRadar Dashboard setup

- Automated GitHub repository market analytics
- Real-time transfer tracking and visualization
- 6-hour update cycle with fresh charts
- Live market insights and M&A signals"

# Создание .gitkeep для charts
mkdir -p charts
touch charts/.gitkeep

# Финальный коммит
git add .
git commit -m "Add charts directory structure"

# Push
echo ""
echo "🚀 Отправляем на GitHub..."
git push origin main

echo ""
echo "✅ Dashboard репозиторий создан!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Перейдите: https://github.com/NickScherbakov/NickScherbakov"
echo "2. Добавьте секрет REPORADAR_URL в Settings > Secrets and variables > Actions"
echo "3. Значение: URL вашего развернутого RepoRadar"
echo "4. Запустите workflow вручную для первого обновления"
echo ""
echo "🎉 Готово! Dashboard будет обновляться автоматически каждые 6 часов"
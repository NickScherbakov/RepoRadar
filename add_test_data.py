#!/usr/bin/env python3
"""Скрипт для добавления тестовых данных в RepoRadar."""

import sqlite3
from datetime import datetime, timedelta
import random

def add_test_data():
    """Добавить тестовые данные о переносах репозиториев."""

    # Список тестовых данных
    test_transfers = [
        {
            'repo': 'facebook/react',
            'old_owner': 'facebook',
            'new_owner': 'meta',
            'date': (datetime.now() - timedelta(days=30)).isoformat(),
            'stars': 180000,
            'language': 'JavaScript'
        },
        {
            'repo': 'microsoft/vscode',
            'old_owner': 'microsoft',
            'new_owner': 'github',
            'date': (datetime.now() - timedelta(days=25)).isoformat(),
            'stars': 120000,
            'language': 'TypeScript'
        },
        {
            'repo': 'google/tensorflow',
            'old_owner': 'google',
            'new_owner': 'tensorflow',
            'date': (datetime.now() - timedelta(days=20)).isoformat(),
            'stars': 160000,
            'language': 'Python'
        },
        {
            'repo': 'apple/swift',
            'old_owner': 'apple',
            'new_owner': 'swiftlang',
            'date': (datetime.now() - timedelta(days=15)).isoformat(),
            'stars': 58000,
            'language': 'Swift'
        },
        {
            'repo': 'netflix/zuul',
            'old_owner': 'netflix',
            'new_owner': 'Netflix-Skunkworks',
            'date': (datetime.now() - timedelta(days=10)).isoformat(),
            'stars': 9500,
            'language': 'Java'
        },
        {
            'repo': 'amazon/aws-sdk-js',
            'old_owner': 'amazon',
            'new_owner': 'aws',
            'date': (datetime.now() - timedelta(days=5)).isoformat(),
            'stars': 6500,
            'language': 'JavaScript'
        },
        {
            'repo': 'stripe/stripe-js',
            'old_owner': 'stripe',
            'new_owner': 'stripe-samples',
            'date': (datetime.now() - timedelta(days=2)).isoformat(),
            'stars': 3200,
            'language': 'TypeScript'
        },
        {
            'repo': 'twilio/twilio-python',
            'old_owner': 'twilio',
            'new_owner': 'twilio-samples',
            'date': (datetime.now() - timedelta(days=1)).isoformat(),
            'stars': 1400,
            'language': 'Python'
        }
    ]

    # Подключение к базе данных
    conn = sqlite3.connect('reporadar.db')
    cursor = conn.cursor()

    # Добавление данных
    for transfer in test_transfers:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO repo_transfers
                (repo, old_owner, new_owner, date, stars, language)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                transfer['repo'],
                transfer['old_owner'],
                transfer['new_owner'],
                transfer['date'],
                transfer['stars'],
                transfer['language']
            ))
            print(f"Добавлен перенос: {transfer['repo']}")
        except Exception as e:
            print(f"Ошибка при добавлении {transfer['repo']}: {e}")

    conn.commit()
    conn.close()
    print(f"Добавлено {len(test_transfers)} тестовых переносов")

if __name__ == '__main__':
    add_test_data()
#!/usr/bin/env python3
"""
Скрипт для добавления поля 'sold' в таблицу stock_item
"""
import sqlite3
import os

# Путь к базе данных
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'sales.db')

if not os.path.exists(db_path):
    print(f"База данных не найдена: {db_path}")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Проверяем, существует ли уже колонка
    cursor.execute("PRAGMA table_info(stock_item)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'sold' in columns:
        print("Колонка 'sold' уже существует в таблице stock_item")
    else:
        # Добавляем колонку
        cursor.execute("ALTER TABLE stock_item ADD COLUMN sold BOOLEAN DEFAULT 0 NOT NULL")
        conn.commit()
        print("Колонка 'sold' успешно добавлена в таблицу stock_item")
    
    conn.close()
    print("Готово!")
    
except Exception as e:
    print(f"Ошибка: {e}")
    exit(1)

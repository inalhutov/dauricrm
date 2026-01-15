#!/usr/bin/env python3
"""
Скрипт для создания таблицы stock_expense
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
    
    # Проверяем, существует ли уже таблица
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stock_expense'")
    if cursor.fetchone():
        print("Таблица 'stock_expense' уже существует")
    else:
        # Создаем таблицу
        cursor.execute("""
            CREATE TABLE stock_expense (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_item_id INTEGER NOT NULL,
                expense_type_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                comment VARCHAR(200),
                FOREIGN KEY (stock_item_id) REFERENCES stock_item(id),
                FOREIGN KEY (expense_type_id) REFERENCES expense_type(id)
            )
        """)
        conn.commit()
        print("Таблица 'stock_expense' успешно создана")
    
    conn.close()
    print("Готово!")
    
except Exception as e:
    print(f"Ошибка: {e}")
    exit(1)

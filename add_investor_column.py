#!/usr/bin/env python3
"""
Скрипт для добавления колонки investor_id в таблицу stock_item.
Использование: python add_investor_column.py
"""
from app import app, db
import sqlite3

def add_investor_column():
    """Добавляет колонку investor_id в таблицу stock_item"""
    with app.app_context():
        print("=" * 50)
        print("Добавление колонки investor_id в таблицу stock_item")
        print("=" * 50)
        
        try:
            # Получаем путь к базе данных
            db_uri = app.config['SQLALCHEMY_DATABASE_URI']
            if db_uri.startswith('sqlite:///'):
                db_path = db_uri.replace('sqlite:///', '')
                # Если относительный путь, ищем в instance/
                if not db_path.startswith('/'):
                    import os
                    instance_path = os.path.join('instance', db_path)
                    if os.path.exists(instance_path):
                        db_path = instance_path
                    elif os.path.exists(db_path):
                        pass  # Используем текущий путь
                    else:
                        # Пробуем найти в разных местах
                        possible_paths = [
                            os.path.join('instance', db_path),
                            db_path,
                            os.path.join('dauricrm', 'instance', db_path)
                        ]
                        for path in possible_paths:
                            if os.path.exists(path):
                                db_path = path
                                break
            
            # Подключаемся к базе данных напрямую
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Проверяем, существует ли колонка
            cursor.execute("PRAGMA table_info(stock_item)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'investor_id' in columns:
                print("\n✅ Колонка investor_id уже существует!")
            else:
                # Добавляем колонку
                print("\nДобавление колонки investor_id...")
                cursor.execute("ALTER TABLE stock_item ADD COLUMN investor_id INTEGER")
                
                # Добавляем внешний ключ (если нужно)
                # SQLite не поддерживает ADD CONSTRAINT, поэтому внешний ключ нужно добавить при создании таблицы
                # Но можно просто добавить колонку, а внешний ключ будет работать через SQLAlchemy
                
                conn.commit()
                print("✅ Колонка investor_id успешно добавлена!")
            
            conn.close()
            
            print("\n" + "=" * 50)
            print("✅ Готово!")
            print("=" * 50)
            
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")
            print("=" * 50)
            raise

if __name__ == '__main__':
    add_investor_column()

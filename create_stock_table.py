#!/usr/bin/env python3
"""
Скрипт для создания таблицы StockItem в базе данных.
Использование: python create_stock_table.py
"""
from app import app, db
from app import StockItem

def create_stock_table():
    """Создает таблицу StockItem в базе данных"""
    with app.app_context():
        print("=" * 50)
        print("Создание таблицы StockItem")
        print("=" * 50)
        
        try:
            # Создаем все таблицы (если их еще нет)
            db.create_all()
            print("\n✅ Таблица StockItem успешно создана!")
            print("=" * 50)
            
            # Проверка
            print("\nПроверка:")
            count = StockItem.query.count()
            print(f"  Записей в таблице StockItem: {count}")
            print("\n" + "=" * 50)
            
        except Exception as e:
            print(f"\n❌ Ошибка при создании таблицы: {e}")
            print("=" * 50)
            raise

if __name__ == '__main__':
    create_stock_table()

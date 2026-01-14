#!/usr/bin/env python3
"""
Скрипт для очистки всех таблиц базы данных.
Использование: python clear_db.py
"""
from app import app, db
from app import City, ExpenseType, Employee, Sale, Expense, GeneralExpense

def clear_database():
    """Очищает все таблицы базы данных"""
    with app.app_context():
        print("=" * 50)
        print("Очистка базы данных")
        print("=" * 50)
        
        # Удаляем данные в правильном порядке (из-за внешних ключей)
        print("\n1. Удаление расходов продаж...")
        count_expense = Expense.query.count()
        Expense.query.delete()
        print(f"   Удалено записей: {count_expense}")
        
        print("\n2. Удаление общих расходов...")
        count_general = GeneralExpense.query.count()
        GeneralExpense.query.delete()
        print(f"   Удалено записей: {count_general}")
        
        print("\n3. Удаление продаж...")
        count_sale = Sale.query.count()
        Sale.query.delete()
        print(f"   Удалено записей: {count_sale}")
        
        print("\n4. Удаление сотрудников...")
        count_employee = Employee.query.count()
        Employee.query.delete()
        print(f"   Удалено записей: {count_employee}")
        
        print("\n5. Удаление типов расходов...")
        count_expense_type = ExpenseType.query.count()
        ExpenseType.query.delete()
        print(f"   Удалено записей: {count_expense_type}")
        
        print("\n6. Удаление городов...")
        count_city = City.query.count()
        City.query.delete()
        print(f"   Удалено записей: {count_city}")
        
        # Сохраняем изменения
        db.session.commit()
        
        print("\n" + "=" * 50)
        print("✅ Все таблицы очищены!")
        print("=" * 50)
        
        # Проверка
        print("\nПроверка (все должно быть 0):")
        print(f"  Продаж: {Sale.query.count()}")
        print(f"  Расходов продаж: {Expense.query.count()}")
        print(f"  Общих расходов: {GeneralExpense.query.count()}")
        print(f"  Городов: {City.query.count()}")
        print(f"  Сотрудников: {Employee.query.count()}")
        print(f"  Типов расходов: {ExpenseType.query.count()}")
        print("\n" + "=" * 50)

if __name__ == '__main__':
    import sys
    
    # Подтверждение
    print("\n⚠️  ВНИМАНИЕ: Это удалит ВСЕ данные из базы данных!")
    response = input("Вы уверены? Введите 'yes' для подтверждения: ")
    
    if response.lower() == 'yes':
        clear_database()
    else:
        print("Операция отменена.")
        sys.exit(0)

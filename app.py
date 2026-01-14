from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sales.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'}

db = SQLAlchemy(app)


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f'<City {self.name}>'


class ExpenseType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f'<ExpenseType {self.name}>'


class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Employee {self.name}>'


class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    photo = db.Column(db.String(200))
    product_name = db.Column(db.String(200), nullable=False)
    reference = db.Column(db.String(200))
    buy_price = db.Column(db.Float, nullable=False)
    sell_price = db.Column(db.Float, nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    city = db.relationship('City', backref='sales')
    employee = db.relationship('Employee', backref='sales')
    expenses = db.relationship('Expense', backref='sale', lazy=True, cascade="all, delete-orphan")

    @property
    def profit(self):
        total_expenses = sum(e.amount for e in self.expenses)
        return self.sell_price - self.buy_price - total_expenses


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sale.id'), nullable=False)
    expense_type_id = db.Column(db.Integer, db.ForeignKey('expense_type.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    comment = db.Column(db.String(200))

    expense_type = db.relationship('ExpenseType', backref='expenses')


class GeneralExpense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    expense_type_id = db.Column(db.Integer, db.ForeignKey('expense_type.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    description = db.Column(db.String(200))

    expense_type = db.relationship('ExpenseType', backref='general_expenses')
    city = db.relationship('City', backref='general_expenses')


class Investor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f'<Investor {self.name}>'


class StockItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'), nullable=False)
    investor_id = db.Column(db.Integer, db.ForeignKey('investor.id'), nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    reference = db.Column(db.String(200))
    buy_price = db.Column(db.Float, nullable=False)
    expected_sell_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, default=1)
    photo = db.Column(db.String(200))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    city = db.relationship('City', backref='stock_items')
    investor = db.relationship('Investor', backref='stock_items')

    @property
    def total_invested(self):
        return self.buy_price * self.quantity

    @property
    def expected_profit(self):
        return (self.expected_sell_price - self.buy_price) * self.quantity


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# ГЛАВНАЯ СТРАНИЦА (MAIN) - корневой маршрут
@app.route('/')
@app.route('/main')
def main():
    return render_template('main.html')


# СТРАНИЦА СТОКА
@app.route('/stock')
def stock():
    # Подсчитываем данные из таблицы StockItem
    all_stock_items = StockItem.query.all()
    total_invested = sum(item.total_invested for item in all_stock_items)
    stock_positions = sum(item.quantity for item in all_stock_items)
    expected_profit = sum(item.expected_profit for item in all_stock_items)
    
    return render_template('stock.html',
                           total_invested=total_invested,
                           stock_positions=stock_positions,
                           expected_profit=expected_profit)


# СТРАНИЦА "ВСЕ ГОРОДА" ДЛЯ СТОКА
@app.route('/stock_cities')
def stock_cities():
    # Получаем все города, у которых есть сток
    cities = City.query.all()
    cities_data = {}
    
    for city in cities:
        stock_items = StockItem.query.filter_by(city_id=city.id).all()
        if stock_items:  # Показываем только города с стоком
            total_invested = sum(item.total_invested for item in stock_items)
            stock_positions = sum(item.quantity for item in stock_items)
            expected_profit = sum(item.expected_profit for item in stock_items)
            
            cities_data[city.name] = {
                'positions': stock_positions,
                'invested': total_invested,
                'expected_profit': expected_profit
            }
    
    # Сортируем города по названию
    sorted_cities = sorted(cities_data.items())
    
    return render_template('stock_cities.html', cities_data=dict(sorted_cities))


# СТРАНИЦА ДЕТАЛЬНОГО СТОКА ПО ГОРОДУ
@app.route('/stock_city/<city_name>')
def stock_city_detail(city_name):
    # Находим город
    city = City.query.filter_by(name=city_name).first_or_404()
    
    # Получаем все товары в стоке для этого города
    stock_items = StockItem.query.filter_by(city_id=city.id).all()
    
    # Подсчитываем общую статистику
    total_invested = sum(item.total_invested for item in stock_items)
    stock_positions = sum(item.quantity for item in stock_items)
    expected_profit = sum(item.expected_profit for item in stock_items)
    
    return render_template('stock_city_detail.html',
                           city=city,
                           stock_items=stock_items,
                           total_invested=total_invested,
                           stock_positions=stock_positions,
                           expected_profit=expected_profit)


# СТРАНИЦА "ВСЕ ИНВЕСТОРЫ" ДЛЯ СТОКА
@app.route('/stock_investors')
def stock_investors():
    # Получаем всех инвесторов, у которых есть сток
    investors = Investor.query.all()
    investors_data = {}
    
    for investor in investors:
        stock_items = StockItem.query.filter_by(investor_id=investor.id).all()
        if stock_items:  # Показываем только инвесторов с стоком
            total_invested = sum(item.total_invested for item in stock_items)
            stock_positions = sum(item.quantity for item in stock_items)
            expected_profit = sum(item.expected_profit for item in stock_items)
            
            # Получаем список уникальных городов для этого инвестора
            cities = sorted(set([item.city.name for item in stock_items]))
            cities_str = ', '.join(cities)
            
            investors_data[investor.name] = {
                'positions': stock_positions,
                'invested': total_invested,
                'expected_profit': expected_profit,
                'cities': cities_str
            }
    
    # Сортируем инвесторов по названию
    sorted_investors = sorted(investors_data.items())
    
    return render_template('stock_investors.html', investors_data=dict(sorted_investors))


# СТРАНИЦА ДЕТАЛЬНОГО СТОКА ПО ИНВЕСТОРУ
@app.route('/stock_investor/<investor_name>')
def stock_investor_detail(investor_name):
    # Находим инвестора
    investor = Investor.query.filter_by(name=investor_name).first_or_404()
    
    # Получаем все товары в стоке для этого инвестора
    stock_items = StockItem.query.filter_by(investor_id=investor.id).all()
    
    # Подсчитываем общую статистику
    total_invested = sum(item.total_invested for item in stock_items)
    stock_positions = sum(item.quantity for item in stock_items)
    expected_profit = sum(item.expected_profit for item in stock_items)
    
    return render_template('stock_investor_detail.html',
                           investor=investor,
                           stock_items=stock_items,
                           total_invested=total_invested,
                           stock_positions=stock_positions,
                           expected_profit=expected_profit)


# СТРАНИЦА DASHBOARD (старая главная)
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    # Получаем параметры периода
    period_type = request.args.get('period_type', 'current_month')  # current_month, custom
    year = request.args.get('year')
    month = request.args.get('month')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Определяем даты фильтра
    if period_type == 'custom' and start_date and end_date:
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
        end = end + relativedelta(days=1)  # чтобы включить конец дня
    else:
        # По умолчанию — текущий месяц
        today = date.today()
        if year and month:
            try:
                selected_date = date(int(year), int(month), 1)
            except:
                selected_date = today
        else:
            selected_date = today

        start = selected_date.replace(day=1)
        end = (start + relativedelta(months=1))

    # Фильтруем продажи за период
    sales = Sale.query.filter(Sale.date >= start, Sale.date < end).all()

    # Расчёты для dashboard
    count_sales = len(sales)
    gross_income = sum(s.sell_price for s in sales)  # Грязный доход
    total_buy = sum(s.buy_price for s in sales)
    total_sale_expenses = sum(sum(e.amount for e in s.expenses) for s in sales)
    general_expenses = GeneralExpense.query.filter(GeneralExpense.date >= start, GeneralExpense.date < end).all()
    total_general_expenses = sum(g.amount for g in general_expenses)
    net_profit = gross_income - total_buy - total_sale_expenses - total_general_expenses

    # Для отображения периода
    months_ru = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
    month_name = months_ru[start.month - 1]
    if period_type == 'custom':
        period_label = f"{start.strftime('%d.%m.%Y')} — {(end - relativedelta(days=1)).strftime('%d.%m.%Y')}"
    else:
        period_label = f"{month_name} {start.year}"

    # Список годов для выбора
    all_years = sorted(set(s.date.year for s in Sale.query.with_entities(Sale.date).all()), reverse=True)
    if not all_years:
        all_years = [date.today().year]

    return render_template('dashboard.html',
                           count_sales=count_sales,
                           gross_income=round(gross_income, 2),
                           net_profit=round(net_profit, 2),
                           period_label=period_label,
                           all_years=all_years,
                           selected_year=start.year,
                           selected_month=start.month,
                           period_type=period_type)


# СТАРАЯ СТРАНИЦА СО СПИСКОМ ПРОДАЖ — теперь на /sales
@app.route('/sales')
def sales():
    # Параметры из запроса
    sort = request.args.get('sort', 'date_desc')
    city_filter = request.args.get('city', 'all')  # 'all' или название города
    year_filter = request.args.get('year', 'all')
    month_filter = request.args.get('month', 'all')

    # Базовый запрос
    sales_query = Sale.query

    # Фильтр по городу
    if city_filter != 'all':
        sales_query = sales_query.join(City).filter(City.name == city_filter)

    # Фильтр по году и месяцу
    if year_filter != 'all':
        try:
            year_int = int(year_filter)
            if month_filter != 'all':
                try:
                    month_int = int(month_filter)
                    start_date = date(year_int, month_int, 1)
                    end_date = start_date + relativedelta(months=1)
                    sales_query = sales_query.filter(Sale.date >= start_date, Sale.date < end_date)
                except:
                    start_date = date(year_int, 1, 1)
                    end_date = date(year_int + 1, 1, 1)
                    sales_query = sales_query.filter(Sale.date >= start_date, Sale.date < end_date)
            else:
                start_date = date(year_int, 1, 1)
                end_date = date(year_int + 1, 1, 1)
                sales_query = sales_query.filter(Sale.date >= start_date, Sale.date < end_date)
        except:
            pass

    # Сортировка
    if sort == 'date_asc':
        sales_query = sales_query.order_by(Sale.date.asc())
    elif sort == 'date_desc':
        sales_query = sales_query.order_by(Sale.date.desc())
    elif sort == 'sell_desc':
        sales_query = sales_query.order_by(Sale.sell_price.desc())
    elif sort == 'sell_asc':
        sales_query = sales_query.order_by(Sale.sell_price.asc())
    elif sort == 'city':
        sales_query = sales_query.join(City).order_by(City.name.asc())
    else:
        sales_query = sales_query.order_by(Sale.date.desc())

    sales = sales_query.all()

    # Сортировка по прибыли в Python
    if sort == 'profit_desc':
        sales.sort(key=lambda s: s.profit, reverse=True)
    elif sort == 'profit_asc':
        sales.sort(key=lambda s: s.profit)

    # Общая прибыль (учитываем фильтр)
    total_profit = sum(s.profit for s in sales)
    
    # Расчет общих расходов за выбранный период
    if year_filter != 'all' and month_filter != 'all':
        try:
            year_int = int(year_filter)
            month_int = int(month_filter)
            start_month = date(year_int, month_int, 1)
            end_month = start_month + relativedelta(months=1)
        except:
            today = date.today()
            start_month = today.replace(day=1)
            end_month = start_month + relativedelta(months=1)
    else:
        today = date.today()
        start_month = today.replace(day=1)
        end_month = start_month + relativedelta(months=1)
    
    # Расходы из продаж за текущий месяц
    # Приводим дату к типу date для корректного сравнения
    def get_sale_date(sale):
        return sale.date.date() if isinstance(sale.date, datetime) else sale.date
    
    sales_this_month = [s for s in sales if start_month <= get_sale_date(s) < end_month]
    total_sale_expenses = sum(sum(e.amount for e in s.expenses) for s in sales_this_month)
    
    # Общие расходы за текущий месяц
    general_expenses_query = GeneralExpense.query.filter(GeneralExpense.date >= start_month, GeneralExpense.date < end_month)
    if city_filter != 'all':
        city_obj = City.query.filter_by(name=city_filter).first()
        if city_obj:
            general_expenses_query = general_expenses_query.filter(GeneralExpense.city_id == city_obj.id)
    general_expenses = general_expenses_query.all()
    total_general_expenses = sum(g.amount for g in general_expenses)
    
    total_expenses = total_sale_expenses + total_general_expenses
    
    # Дополнительные метрики
    count_sales = len(sales_this_month)
    gross_income = sum(s.sell_price for s in sales_this_month)
    total_buy = sum(s.buy_price for s in sales_this_month)
    net_profit_month = gross_income - total_buy - total_expenses
    
    # Период для отображения
    months_ru = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
    month_name = months_ru[start_month.month - 1]
    period_label = f"{month_name} {start_month.year}"

    # Список всех уникальных городов для фильтра
    all_cities = sorted([c.name for c in City.query.all()])
    
    # Список всех годов для фильтра
    all_years = sorted(set(s.date.year for s in Sale.query.with_entities(Sale.date).all()), reverse=True)
    if not all_years:
        all_years = [date.today().year]

    return render_template('index.html',
                           sales=sales,
                           total_profit=round(total_profit, 2),
                           sort=sort,
                           city_filter=city_filter,
                           year_filter=year_filter if year_filter != 'all' else 'all',
                           month_filter=month_filter if month_filter != 'all' else 'all',
                           all_cities=all_cities,
                           all_years=all_years,
                           months_ru=months_ru,
                           total_expenses=round(total_expenses, 2),
                           count_sales=count_sales,
                           gross_income=round(gross_income, 2),
                           net_profit_month=round(net_profit_month, 2),
                           period_label=period_label)


@app.route('/add_sale', methods=['GET', 'POST'])
def add_sale():
    cities = City.query.all()
    expense_types = ExpenseType.query.all()
    employees = Employee.query.all()

    if request.method == 'POST':
        product_name = request.form['product_name']
        reference = request.form.get('reference', '')
        buy_price = float(request.form['buy_price'])
        sell_price = float(request.form['sell_price'])
        city_id = int(request.form['city_id'])
        employee_id = int(request.form['employee_id'])
        date_str = request.form['date']
        date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else datetime.utcnow()

        photo_path = None
        photo = request.files['photo']
        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            photo_path = filename
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        new_sale = Sale(photo=photo_path, product_name=product_name, reference=reference,
                        buy_price=buy_price, sell_price=sell_price,
                        city_id=city_id, employee_id=employee_id, date=date)
        db.session.add(new_sale)
        db.session.commit()

        # Добавление расходов
        expense_type_ids = request.form.getlist('expense_type_id')
        amounts = request.form.getlist('expense_amount')
        comments = request.form.getlist('expense_comment')
        for et_id, amt, comment in zip(expense_type_ids, amounts, comments):
            if et_id and amt:
                expense = Expense(sale_id=new_sale.id, expense_type_id=int(et_id), amount=float(amt), comment=comment if comment else None)
                db.session.add(expense)

        db.session.commit()
        flash('Продажа добавлена!', 'success')
        return redirect(url_for('sales'))

    return render_template('add_sale.html', cities=cities, expense_types=expense_types, employees=employees)


@app.route('/add_stock', methods=['GET', 'POST'])
def add_stock():
    cities = City.query.all()
    expense_types = ExpenseType.query.all()
    investors = Investor.query.all()

    if request.method == 'POST':
        product_name = request.form['product_name']
        reference = request.form.get('reference', '')
        buy_price = float(request.form['buy_price'])
        expected_sell_price = float(request.form['expected_sell_price'])
        city_id = int(request.form['city_id'])
        investor_id = int(request.form['investor_id'])

        photo_path = None
        photo = request.files['photo']
        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            photo_path = filename
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        new_stock = StockItem(
            photo=photo_path,
            product_name=product_name,
            reference=reference,
            buy_price=buy_price,
            expected_sell_price=expected_sell_price,
            city_id=city_id,
            investor_id=investor_id
        )
        db.session.add(new_stock)
        db.session.commit()

        # Добавление расходов (если будут нужны в будущем)
        # expense_type_ids = request.form.getlist('expense_type_id')
        # amounts = request.form.getlist('expense_amount')
        # comments = request.form.getlist('expense_comment')
        # for et_id, amt, comment in zip(expense_type_ids, amounts, comments):
        #     if et_id and amt:
        #         # Можно создать отдельную таблицу StockExpense если нужно
        #         pass

        db.session.commit()
        flash('Сток добавлен!', 'success')
        return redirect(url_for('stock'))

    return render_template('add_stock.html', cities=cities, expense_types=expense_types, investors=investors)


@app.route('/edit_sale/<int:sale_id>', methods=['GET', 'POST'])
def edit_sale(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    cities = City.query.all()
    expense_types = ExpenseType.query.all()
    employees = Employee.query.all()

    if request.method == 'POST':
        sale.product_name = request.form['product_name']
        sale.reference = request.form.get('reference', '')
        sale.buy_price = float(request.form['buy_price'])
        sale.sell_price = float(request.form['sell_price'])
        sale.city_id = int(request.form['city_id'])
        sale.employee_id = int(request.form['employee_id'])
        date_str = request.form['date']
        sale.date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else datetime.utcnow()

        photo = request.files['photo']
        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            sale.photo = filename

        # Обновление расходов
        for exp in sale.expenses:
            db.session.delete(exp)
        expense_type_ids = request.form.getlist('expense_type_id')
        amounts = request.form.getlist('expense_amount')
        for et_id, amt in zip(expense_type_ids, amounts):
            if et_id and amt:
                expense = Expense(sale_id=sale.id, expense_type_id=int(et_id), amount=float(amt))
                db.session.add(expense)

        db.session.commit()
        flash('Продажа обновлена!', 'success')
        return redirect(url_for('sales'))

    return render_template('edit_sale.html', sale=sale, cities=cities, expense_types=expense_types, employees=employees)


@app.route('/delete_sale/<int:sale_id>', methods=['POST'])
def delete_sale(sale_id):
    sale = Sale.query.get_or_404(sale_id)

    if sale.photo:
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], sale.photo)
        if os.path.exists(photo_path):
            os.remove(photo_path)

    db.session.delete(sale)
    db.session.commit()
    flash('Продажа удалена!', 'success')
    return redirect(url_for('sales'))


@app.route('/stats', methods=['GET', 'POST'])
def stats():
    # Параметры периода и города
    period_type = request.args.get('period_type', 'current_month')
    year = request.args.get('year')
    month = request.args.get('month')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    city_filter = request.args.get('city', 'all')

    # Определяем даты
    if period_type == 'custom' and start_date and end_date:
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
        end = end + relativedelta(days=1)
    else:
        today = date.today()
        if year and month:
            try:
                selected_date = date(int(year), int(month), 1)
            except:
                selected_date = today
        else:
            selected_date = today
        start = selected_date.replace(day=1)
        end = start + relativedelta(months=1)

    # Фильтры для продаж и расходов
    sales_query = Sale.query.filter(Sale.date >= start, Sale.date < end)
    general_exp_query = GeneralExpense.query.filter(GeneralExpense.date >= start, GeneralExpense.date < end)

    if city_filter != 'all':
        sales_query = sales_query.filter(Sale.city_id == City.query.filter_by(name=city_filter).first().id)
        general_exp_query = general_exp_query.filter(GeneralExpense.city_id == City.query.filter_by(name=city_filter).first().id)

    sales = sales_query.all()
    general_expenses = general_exp_query.all()

    # Группируем расходы по датам
    expenses_by_date = {}
    total_expenses = 0
    
    # Расходы из продаж (используем дату продажи)
    for s in sales:
        sale_date = s.date.date() if isinstance(s.date, datetime) else s.date
        if sale_date not in expenses_by_date:
            expenses_by_date[sale_date] = []
        for e in s.expenses:
            expenses_by_date[sale_date].append({
                'type': e.expense_type.name,
                'amount': e.amount,
                'description': e.comment,  # Комментарий из расходов продажи
                'is_sale_expense': True
            })
            total_expenses += e.amount
    
    # Общие расходы (используем дату расхода)
    for g in general_expenses:
        exp_date = g.date.date() if isinstance(g.date, datetime) else g.date
        if exp_date not in expenses_by_date:
            expenses_by_date[exp_date] = []
        expenses_by_date[exp_date].append({
            'type': g.expense_type.name,
            'amount': g.amount,
            'description': g.description,  # Комментарий для общих расходов
            'is_sale_expense': False
        })
        total_expenses += g.amount
    
    # Сортируем даты по убыванию (новые сначала)
    sorted_expenses_by_date = sorted(expenses_by_date.items(), key=lambda x: x[0], reverse=True)

    # Общая чистая прибыль (для полноты, но фокус на расходах)
    gross_income = sum(s.sell_price for s in sales)
    total_buy = sum(s.buy_price for s in sales)
    net_profit = gross_income - total_buy - total_expenses

    # Период лейбл
    months_ru = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
    month_name = months_ru[start.month - 1]
    if period_type == 'custom':
        period_label = f"{start.strftime('%d.%m.%Y')} — {(end - relativedelta(days=1)).strftime('%d.%m.%Y')}"
    else:
        period_label = f"{month_name} {start.year}"

    all_years = sorted(set(s.date.year for s in Sale.query.with_entities(Sale.date).all()), reverse=True)
    if not all_years:
        all_years = [date.today().year]
    all_cities = sorted([c.name for c in City.query.all()])

    expense_types = ExpenseType.query.all()
    cities = City.query.all()

    return render_template('stats.html',
                           total_expenses=round(total_expenses, 2),
                           expenses_by_date=sorted_expenses_by_date,
                           period_label=period_label,
                           all_years=all_years,
                           selected_year=start.year,
                           selected_month=start.month,
                           period_type=period_type,
                           city_filter=city_filter,
                           all_cities=all_cities,
                           expense_types=expense_types,
                           cities=cities,
                           net_profit=round(net_profit, 2))


# Добавление общего расхода
@app.route('/add_general_expense', methods=['POST'])
def add_general_expense():
    expense_type_id = int(request.form['expense_type_id'])
    amount = float(request.form['amount'])
    date_str = request.form['date']
    date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else datetime.utcnow()
    city_id = int(request.form['city_id']) if request.form['city_id'] != 'none' else None
    description = request.form.get('description', '')

    new_gen_exp = GeneralExpense(expense_type_id=expense_type_id, amount=amount, date=date, city_id=city_id, description=description)
    db.session.add(new_gen_exp)
    db.session.commit()
    flash('Общий расход добавлен!', 'success')
    return redirect(url_for('stats'))


# Маршруты для добавления городов, типов расходов и сотрудников (без изменений)
@app.route('/add_city', methods=['POST'])
def add_city():
    name = request.form['name'].strip()
    if name and not City.query.filter_by(name=name).first():
        new_city = City(name=name)
        db.session.add(new_city)
        db.session.commit()
        flash('Город добавлен!', 'success')
    else:
        flash('Город уже существует или пустое имя.', 'error')
    return redirect(request.referrer or url_for('add_sale'))


@app.route('/add_expense_type', methods=['POST'])
def add_expense_type():
    name = request.form['name'].strip()
    if name and not ExpenseType.query.filter_by(name=name).first():
        new_type = ExpenseType(name=name)
        db.session.add(new_type)
        db.session.commit()
        flash('Тип расхода добавлен!', 'success')
    else:
        flash('Тип уже существует или пустое имя.', 'error')
    return redirect(request.referrer or url_for('add_sale'))


@app.route('/add_employee', methods=['POST'])
def add_employee():
    name = request.form['name'].strip()
    if name:
        new_employee = Employee(name=name)
        db.session.add(new_employee)
        db.session.commit()
        flash('Сотрудник добавлен!', 'success')
    else:
        flash('Пустое имя.', 'error')
    return redirect(request.referrer or url_for('add_sale'))


@app.route('/add_investor', methods=['POST'])
def add_investor():
    name = request.form['name'].strip()
    if name and not Investor.query.filter_by(name=name).first():
        new_investor = Investor(name=name)
        db.session.add(new_investor)
        db.session.commit()
        flash('Инвестор добавлен!', 'success')
    else:
        flash('Инвестор уже существует или пустое имя.', 'error')
    return redirect(request.referrer or url_for('add_stock'))


@app.route('/all_sales_summary')
def all_sales_summary():
    # Получаем параметры фильтрации
    year_filter = request.args.get('year', 'all')
    month_filter = request.args.get('month', 'all')
    city_filter = request.args.get('city', 'all')

    # Базовый запрос
    sales_query = Sale.query

    # Фильтр по году и месяцу
    if year_filter != 'all':
        try:
            year_int = int(year_filter)
            if month_filter != 'all':
                try:
                    month_int = int(month_filter)
                    start_date = date(year_int, month_int, 1)
                    end_date = start_date + relativedelta(months=1)
                except:
                    start_date = date(year_int, 1, 1)
                    end_date = date(year_int + 1, 1, 1)
            else:
                start_date = date(year_int, 1, 1)
                end_date = date(year_int + 1, 1, 1)
            sales_query = sales_query.filter(Sale.date >= start_date, Sale.date < end_date)
        except:
            pass

    # Фильтр по городу
    if city_filter != 'all':
        sales_query = sales_query.join(City).filter(City.name == city_filter)

    # Получаем все продажи
    all_sales = sales_query.all()

    # Группируем данные по городам и месяцам
    cities_data = {}

    for sale in all_sales:
        city_name = sale.city.name
        sale_date = sale.date.date() if isinstance(sale.date, datetime) else sale.date
        sale_month = sale_date.month
        sale_year = sale_date.year
        
        if city_name not in cities_data:
            cities_data[city_name] = {
                'count': 0,
                'total_buy': 0,
                'total_sell': 0,
                'total_expenses': 0,
                'gross_profit': 0,
                'net_profit': 0,
                'months': {}  # Группировка по месяцам
            }

        # Обновляем статистику города
        data = cities_data[city_name]
        data['count'] += 1
        data['total_buy'] += sale.buy_price
        data['total_sell'] += sale.sell_price

        # Расходы этой продажи
        sale_expenses = sum(e.amount for e in sale.expenses)
        data['total_expenses'] += sale_expenses
        
        # Группировка по месяцам
        month_key = f"{sale_year}-{sale_month:02d}"
        if month_key not in data['months']:
            data['months'][month_key] = {
                'count': 0,
                'gross_profit': 0,
                'net_profit': 0,
                'month': sale_month,
                'year': sale_year
            }
        
        month_data = data['months'][month_key]
        month_data['count'] += 1
        month_data['gross_profit'] += (sale.sell_price - sale.buy_price)
        month_data['net_profit'] += (sale.sell_price - sale.buy_price - sale_expenses)
    
    # Вычисляем итоговые прибыли и сортируем месяцы для каждого города
    for city_name, data in cities_data.items():
        data['gross_profit'] = data['total_sell'] - data['total_buy']
        data['net_profit'] = data['gross_profit'] - data['total_expenses']
        data['months'] = dict(sorted(data['months'].items(), reverse=True))
    
    # Период для отображения
    months_ru = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
    period_label = "Все продажи"
    if year_filter != 'all' and month_filter != 'all':
        try:
            month_name = months_ru[int(month_filter) - 1]
            period_label = f"{month_name} {year_filter}"
        except:
            period_label = f"{year_filter} год"
    elif year_filter != 'all':
        period_label = f"{year_filter} год"

    # Список годов для фильтра
    all_years = sorted(set(s.date.year for s in Sale.query.with_entities(Sale.date).all()), reverse=True)
    if not all_years:
        all_years = [date.today().year]
    all_cities = sorted([c.name for c in City.query.all()])

    return render_template('all_sales_summary.html',
                           cities_data=cities_data,
                           all_years=all_years,
                           all_cities=all_cities,
                           selected_year=year_filter,
                           selected_month=month_filter,
                           selected_city=city_filter,
                           period_label=period_label,
                           months_ru=months_ru)


if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    with app.app_context():
        db.create_all()
    app.run(debug=True)
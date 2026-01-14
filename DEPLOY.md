# Инструкция по развертыванию Flask приложения на Ubuntu сервере

## Предварительные требования

- Ubuntu сервер (20.04 или новее)
- Домен, настроенный на IP адрес вашего сервера
- SSH доступ к серверу
- Рутовый доступ (sudo)

---

## Шаг 1: Подготовка сервера

### 1.1 Обновление системы

```bash
sudo apt update
sudo apt upgrade -y
```

### 1.2 Установка необходимых пакетов

```bash
sudo apt install -y python3-pip python3-venv nginx git ufw
```

### 1.3 Настройка файрвола

```bash
# Разрешаем SSH (убедитесь, что порт правильный!)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status
```

---

## Шаг 2: Создание пользователя для приложения (опционально, но рекомендуется)

```bash
# Создаем нового пользователя
sudo adduser --disabled-password --gecos "" dauricrm

# Переключаемся на нового пользователя
sudo su - dauricrm
```

---

## Шаг 3: Загрузка проекта на сервер через SCP

### 3.1 Подготовка на сервере (ОБЯЗАТЕЛЬНО!)

**Сначала подключитесь к серверу по SSH и создайте директорию:**

```bash
# Подключитесь к серверу
ssh root@ваш_IP_или_домен
# или
ssh ваш_пользователь@ваш_IP_или_домен

# После подключения создайте директорию
mkdir -p /home/root/dauricrm

# Или если используете другого пользователя (например, ubuntu)
mkdir -p /home/ubuntu/dauricrm

# Проверьте, что директория создана
ls -la /home/root/  # или /home/ubuntu/

# Выйдите из SSH (нажмите Ctrl+D или введите exit)
```

**Важно:** Директория должна быть создана ДО выполнения команды scp!

### 3.2 Загрузка проекта с вашего локального компьютера

**⚠️ ВАЖНО: Загружайте СОДЕРЖИМОЕ папки, а не саму папку!**

**Для Windows (PowerShell или Git Bash):**

```bash
# Перейдите ВНУТРЬ папки dauricrm на вашем компьютере
cd C:\Users\79024\PycharmProjects\dubai\dauricrm

# Загрузите ВСЁ СОДЕРЖИМОЕ (все файлы и папки) на сервер
scp -r * root@ваш_IP:/home/root/dauricrm/

# Или если нужно загрузить и скрытые файлы тоже:
scp -r . root@ваш_IP:/home/root/dauricrm/
```

**АЛЬТЕРНАТИВНЫЙ СПОСОБ (из папки dubai):**

```bash
# Останьтесь в папке dubai и используйте правильный синтаксис
cd C:\Users\79024\PycharmProjects\dubai

# Загрузите содержимое папки dauricrm (обратите внимание на ./*)
scp -r dauricrm/* root@ваш_IP:/home/root/dauricrm/

# Или так (создаст правильную структуру):
scp -r dauricrm root@ваш_IP:/home/root/
# Это создаст /home/root/dauricrm со всеми файлами внутри
```

**Для Linux/Mac:**

```bash
# Перейдите в папку с проектом
cd ~/PycharmProjects/dubai

# Загрузите проект на сервер
scp -r dauricrm/ пользователь@IP_вашего_сервера:/home/пользователь/dauricrm
```

**Пример команды (замените на свои данные):**

```bash
# Вариант 1: После создания директории на сервере (см. шаг 3.1)
scp -r dauricrm/ root@123.45.67.89:/home/root/dauricrm

# Вариант 2: Загрузка в домашнюю директорию (она всегда существует!)
scp -r dauricrm/ root@123.45.67.89:~/
# На сервере потом: mv ~/dauricrm /home/root/dauricrm

# Вариант 3: Загрузка во временную папку /tmp (она всегда существует)
scp -r dauricrm/ root@123.45.67.89:/tmp/dauricrm
# На сервере потом: mv /tmp/dauricrm /home/root/dauricrm
```

**Или с использованием SSH ключа (рекомендуется):**

```bash
scp -i ~/.ssh/your_key.pem -r dauricrm/ root@сервер:~/
```

**✅ ПРАВИЛЬНОЕ РЕШЕНИЕ (если директория уже создана на сервере):**

**Вариант 1: Загрузить содержимое папки (РЕКОМЕНДУЕТСЯ)**

```bash
# С вашего Windows компьютера в PowerShell
cd C:\Users\79024\PycharmProjects\dubai

# Загрузите СОДЕРЖИМОЕ папки dauricrm (обратите внимание на /* в конце!)
scp -r dauricrm/* root@ваш_IP:/home/root/dauricrm/

# Если нужно загрузить и скрытые файлы (например .gitignore), используйте:
cd dauricrm
scp -r * root@ваш_IP:/home/root/dauricrm/
```

**Вариант 2: Загрузить всю папку в родительскую директорию**

```bash
# С вашего Windows компьютера
cd C:\Users\79024\PycharmProjects\dubai

# Загрузите папку dauricrm в /home/root/ (обратите внимание: БЕЗ /dauricrm в конце пути!)
scp -r dauricrm root@ваш_IP:/home/root/

# Это создаст /home/root/dauricrm со всеми файлами внутри
# Если на сервере уже есть пустая папка, удалите её сначала:
# ssh root@ваш_IP
# rm -rf /home/root/dauricrm
# exit
# И потом загрузите заново
```

**Вариант 3: Загрузить в домашнюю директорию, потом переместить**

```bash
# С вашего Windows компьютера
cd C:\Users\79024\PycharmProjects\dubai
scp -r dauricrm root@ваш_IP:~/

# Потом на сервере
ssh root@ваш_IP
rm -rf /home/root/dauricrm  # Удалите пустую папку, если она есть
mv ~/dauricrm /home/root/
```

### 3.3 Альтернатива: Создание архива и загрузка

Если SCP работает медленно, можно создать архив:

**На вашем компьютере (Windows PowerShell):**

```powershell
# Создайте архив (без виртуального окружения и БД)
cd C:\Users\79024\PycharmProjects\dubai
Compress-Archive -Path dauricrm\app.py,dauricrm\templates,dauricrm\uploads,dauricrm\wsgi.py,dauricrm\main.py,dauricrm\README.md -DestinationPath dauricrm.zip -Force
```

**На вашем компьютере (Linux/Mac):**

```bash
cd ~/PycharmProjects/dubai
tar -czf dauricrm.tar.gz dauricrm/ --exclude='dauricrm/venv' --exclude='dauricrm/instance' --exclude='dauricrm/__pycache__'
```

**Загрузите архив:**

```bash
scp dauricrm.zip пользователь@сервер:/home/пользователь/
# или
scp dauricrm.tar.gz пользователь@сервер:/home/пользователь/
```

**На сервере распакуйте:**

```bash
# Для zip
cd /home/пользователь
unzip dauricrm.zip -d dauricrm

# Для tar.gz
cd /home/пользователь
tar -xzf dauricrm.tar.gz
```

### 3.4 Проверка загрузки

На сервере проверьте, что файлы загружены:

```bash
cd /home/пользователь/dauricrm  # или /home/dauricrm/dauricrm
ls -la
# Должны быть видны: app.py, templates/, uploads/, wsgi.py и т.д.
```

---

## Шаг 4: Настройка приложения

### 4.1 Создание виртуального окружения

```bash
cd /home/dauricrm/dauricrm  # или путь к вашему проекту
python3 -m venv venv
source venv/bin/activate
```

### 4.2 Установка зависимостей

```bash
# Сначала обновляем pip
pip install --upgrade pip

# Устанавливаем зависимости
pip install -r requirements

# Устанавливаем Gunicorn для production
pip install gunicorn
```

### 4.3 Настройка конфигурации

Отредактируйте `app.py` и измените SECRET_KEY на случайный:

```python
import secrets
print(secrets.token_hex(32))  # Запустите это в Python для генерации ключа
```

Замените в `app.py`:
```python
app.config['SECRET_KEY'] = 'сгенерированный_ключ_здесь'
```

### 4.4 Создание необходимых директорий и файлов

```bash
# Убедитесь, что папки существуют
mkdir -p instance uploads

# Инициализация базы данных
python3 -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### 4.5 Настройка прав доступа

```bash
# Устанавливаем правильные права
chmod -R 755 /home/dauricrm/dauricrm
chmod -R 777 instance uploads  # Для записи БД и файлов
```

---

## Шаг 5: Настройка Gunicorn

### 5.1 Создание WSGI точки входа

Создайте файл `wsgi.py` в корне проекта (`dauricrm/wsgi.py`):

```python
#!/usr/bin/env python3
import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(__file__))

from app import app

if __name__ == "__main__":
    app.run()
```

### 5.2 Тестирование Gunicorn

```bash
cd /home/dauricrm/dauricrm
source venv/bin/activate
gunicorn --bind 0.0.0.0:8000 wsgi:app
```

Если всё работает, нажмите Ctrl+C для остановки.

### 5.3 Создание systemd сервиса

Создайте файл `/etc/systemd/system/dauricrm.service`:

```bash
sudo nano /etc/systemd/system/dauricrm.service
```

Вставьте следующее содержимое:

```ini
[Unit]
Description=Gunicorn instance to serve dauricrm
After=network.target

[Service]
User=dauricrm
Group=www-data
WorkingDirectory=/home/dauricrm/dauricrm
Environment="PATH=/home/dauricrm/dauricrm/venv/bin"
ExecStart=/home/dauricrm/dauricrm/venv/bin/gunicorn --workers 3 --bind unix:/home/dauricrm/dauricrm/dauricrm.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
```

**Внимание:** Замените `dauricrm` на ваше имя пользователя и проверьте пути!

### 5.4 Запуск и включение сервиса

```bash
sudo systemctl daemon-reload
sudo systemctl start dauricrm
sudo systemctl enable dauricrm
sudo systemctl status dauricrm
```

Проверьте, что сервис работает без ошибок.

---

## Шаг 6: Настройка Nginx

### 6.1 Создание конфигурации Nginx

Создайте файл `/etc/nginx/sites-available/dauricrm`:

```bash
sudo nano /etc/nginx/sites-available/dauricrm
```

Вставьте следующее (замените `yourdomain.com` на ваш домен):

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    client_max_body_size 50M;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/dauricrm/dauricrm/dauricrm.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /home/dauricrm/dauricrm/static;
    }
}
```

### 6.2 Активация конфигурации

```bash
# Создаем символическую ссылку
sudo ln -s /etc/nginx/sites-available/dauricrm /etc/nginx/sites-enabled/

# Проверяем конфигурацию
sudo nginx -t

# Перезапускаем Nginx
sudo systemctl restart nginx
```

---

## Шаг 7: Настройка SSL сертификата (Let's Encrypt)

### 7.1 Установка Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 7.2 Получение SSL сертификата

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

Certbot автоматически настроит Nginx для использования HTTPS и будет обновлять сертификат автоматически.

### 7.3 Проверка автопродления

```bash
sudo certbot renew --dry-run
```

---

## Шаг 8: Финальная проверка

1. Откройте браузер и перейдите на `https://yourdomain.com`
2. Проверьте логи приложения:
   ```bash
   sudo journalctl -u dauricrm -f
   ```
3. Проверьте логи Nginx:
   ```bash
   sudo tail -f /var/log/nginx/error.log
   ```

---

## Шаг 9: Настройка автоматических резервных копий (рекомендуется)

Создайте скрипт для резервного копирования базы данных:

```bash
sudo nano /home/dauricrm/backup.sh
```

Содержимое скрипта:

```bash
#!/bin/bash
BACKUP_DIR="/home/dauricrm/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Бэкап базы данных
cp /home/dauricrm/dauricrm/instance/sales.db $BACKUP_DIR/sales_$DATE.db

# Бэкап загруженных файлов
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /home/dauricrm/dauricrm/uploads

# Удаляем старые бэкапы (старше 30 дней)
find $BACKUP_DIR -type f -mtime +30 -delete
```

Сделайте скрипт исполняемым:

```bash
chmod +x /home/dauricrm/backup.sh
```

Добавьте в crontab для автоматического запуска каждый день:

```bash
crontab -e
```

Добавьте строку:

```
0 2 * * * /home/dauricrm/backup.sh
```

---

## Полезные команды для управления

### Перезапуск приложения

```bash
sudo systemctl restart dauricrm
```

### Просмотр логов

```bash
sudo journalctl -u dauricrm -f
```

### Остановка/Запуск Nginx

```bash
sudo systemctl stop nginx
sudo systemctl start nginx
sudo systemctl restart nginx
```

### Обновление приложения

```bash
cd /home/dauricrm/dauricrm
source venv/bin/activate
git pull  # или загрузите новые файлы
pip install -r requirements
sudo systemctl restart dauricrm
```

---

## Решение проблем

### Если приложение не запускается:

1. Проверьте логи: `sudo journalctl -u dauricrm -n 50`
2. Проверьте права доступа к файлам
3. Убедитесь, что порт не занят: `sudo netstat -tulpn | grep :8000`
4. Проверьте конфигурацию Nginx: `sudo nginx -t`

### Если Nginx возвращает 502 Bad Gateway:

1. Проверьте, что Gunicorn запущен: `sudo systemctl status dauricrm`
2. Проверьте права на socket файл
3. Проверьте логи Nginx: `sudo tail -f /var/log/nginx/error.log`

### Если не работает загрузка файлов:

1. Проверьте права на папку uploads: `chmod -R 777 uploads`
2. Проверьте, что путь правильный в app.py

---

## Безопасность

1. **Никогда не коммитьте SECRET_KEY в Git!**
2. Используйте переменные окружения для чувствительных данных
3. Регулярно обновляйте систему: `sudo apt update && sudo apt upgrade`
4. Настройте fail2ban для защиты от брутфорса:
   ```bash
   sudo apt install fail2ban
   sudo systemctl enable fail2ban
   ```
5. Рассмотрите возможность использования PostgreSQL вместо SQLite для production

---

## Дополнительная настройка (опционально)

### Использование переменных окружения

Создайте файл `.env` в корне проекта:

```bash
FLASK_ENV=production
SECRET_KEY=ваш_секретный_ключ
DATABASE_URI=sqlite:///sales.db
```

Установите python-dotenv:
```bash
pip install python-dotenv
```

И обновите app.py для чтения переменных окружения.

---

Готово! Ваше приложение должно быть доступно по адресу https://yourdomain.com

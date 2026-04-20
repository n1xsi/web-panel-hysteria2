<h1 align="center">
    
⚡ Hysteria2 Lightweight Web Panel

[![Python](https://custom-icon-badges.demolab.com/badge/3.12+-ffbc00?style=for-the-badge&logo=pythonn&label=python&labelColor=303030)](#)
[![Flask](https://img.shields.io/badge/3.1.3-ffbc00?style=for-the-badge&logo=flask&logoColor=3db4cd&label=flask&labelColor=303030)](#)
[![ruamel.yaml](https://custom-icon-badges.demolab.com/badge/0.19.1-ffbc00?style=for-the-badge&logo=ruamel.yaml&logoColor=3db4cd&label=ruamel.yaml&labelColor=303030)](#)

</h1>

<p align="center">
    <img src="https://i.imgur.com/CjXrCyy.jpeg" width="50%">
</p>

Простенькая и легковесная веб-панель управления пользователями для VPN-сервера на базе [Hysteria2](https://v2.hysteria.network/).

## 📌 Особенности
*   📝 **Генерация конфигураций:** Генерация ссылок и `.yaml`-конфигов (Clash/Mihomo/Clash Meta) на основе вашего шаблона (`config.yaml`).
*   🔗 **Генерация ссылок `hy2://`:** Напротив каждой ссылки есть кнопка для копирования, оснащённая fallback-скриптом на JavaScript, который позволяет копировать ссылки даже если панель работает по HTTP без SSL-сертификата.
*   🕒 **Отложенная перезагрузка:** Скрипт перезагружает службу `hysteria-server.service` с небольшой задержкой. Если вы сидите через свой же VPN, страница в браузере успеет обновиться до того, как VPN-соединение кратковременно разорвётся.
*   🔐 **Безопасность**: Доступ к панели защищён через Basic Auth (логин/пароль).

## 🏋🏻‍♀️ Какую рутину это оптимизирует
Если у вас стоит базовый протокол **Hysteria2**, то скорее всего ваш путь выглядит так:
1) Подключение к серверу через `ssh`;
2) Генерирация и копирование ключа через `openssl rand -hex 16`;
3) Открытие с конфига через `nano /etc/hysteria/config.yaml`;
4) Запись в конец списка `userpass: ...` нового пользователя ("ИМЯ: СКОПИРОВАННЫЙ_КЛЮЧ");
5) Сохранение файла и выход;
6) Обновление службы `hysteria-server.service` через `systemctl restart hysteria-server.service`;
7) Переход на [сайт генератора конфигов](https://hysteriaconfig.xyz/);
8) Копирование ключа и файла и отсыл пользователю.

<br>

С данной web-панелью: вы просто заходите на сайт → вписываете имя конфига → копируете готовый конфиг.

## 🏗️ Как установить

### 1. Подготовка
На сервере (Ubuntu/Debian) должны быть установлены Python3 и `venv`:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv git -y
```

### 2. Клонирование репозитория
```bash
sudo git clone https://github.com/n1xsi/web-panel-hysteria2.git /opt/hysteria-panel
cd /opt/hysteria-panel
```

### 3. Установка зависимостей
Создаём виртуальное окружение и устанавливаем нужные библиотеки:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Настройка панели
Откройте файл `app.py`:
```bash
nano app.py
```

Отредактируйте настройки в начале файла (строки 13-21):
```python
# --- НАСТРОЙКИ ---
app.config['BASIC_AUTH_USERNAME'] = 'admin'      # Ваш логин от панели
app.config['BASIC_AUTH_PASSWORD'] = 'superpass'  # Ваш пароль от панели

# --- ПУТИ ---
SERVER_CONFIG_PATH = '/etc/hysteria/config.yaml' # Путь к конфигу Hysteria
CLIENT_TEMPLATE_PATH = '/opt/hysteria-panel/client_template.yaml'
DOMAIN = 'example.com'                           # Замените на ваш домен!
```

### 5. Настройка шаблона клиента
Отредактируйте файл `client_template.yaml` под ваши нужды (добавить нужные правила маршрутизации / настройки обфускации). Замените строки `server: example.com` и `sni: example.com` (64 и 67 строки) на ваши данные.

**Главное: В месте, где должен быть пароль пользователя, обязательно оставьте плейсхолдер {{ auth_str }}.**

### 6. Запуск в фоновом режиме (Systemd)
Чтобы панель работала всегда и запускалась после перезагрузки сервера:
```bash
sudo nano /etc/systemd/system/hysteria-panel.service
```

Вставьте конфигурацию:
```
[Unit]
Description=Hysteria2 Web Admin Panel
After=network.target

[Service]
User=root
WorkingDirectory=/opt/hysteria-panel
ExecStart=/opt/hysteria-panel/venv/bin/python /opt/hysteria-panel/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Запускаем службу:
```bash
sudo systemctl daemon-reload
sudo systemctl enable hysteria-panel
sudo systemctl start hysteria-panel
```

## 👉 Использование
1. Откройте в браузере `http://IP_ВАШЕГО_СЕРВЕРА:8080`
2. Введите логин и пароль, указанные в `app.py`
3. Добавляете пользователей -> перезагружается служба `hysteria-server.service`


## 📝 Требования к конфигу Hysteria2
Скрипт ожидает, что в вашем `/etc/hysteria/config.yaml` используется метод авторизации `userpass`. Пример структуры:
```yaml
listen: 0.0.0.0:443

acme:
    type: http
    domains:
        - example.com
    email: admin@example.com

auth:
    type: userpass
    userpass:
        User1: password123
        User2: password456

masquerade:
    type: file
    file:
        dir: /var/www/masq
    listenHTTP: :80
    listenHTTPS: :443
    forceHTTPS: true
```

## 🗑️ Удаление hysteria2 и панели
Если вы хотите удалить Hysteria2 и панель, выполните следующие действия:

### 1. Удаление Hysteria2
Остановка и отключение службы:
```bash
sudo systemctl stop hysteria-server
sudo systemctl disable hysteria-server
```

Удаление программного обеспечения:
```bash
sudo apt-get purge hysteria -y
sudo rm /usr/local/bin/hysteria
```

Удаление директории с конфигурацияими:
```bash
sudo rm -rf /etc/hysteria/
```

### 2. Удаление веб-панели
Остановка и отключение:
```bash
sudo systemctl stop hysteria-panel
sudo systemctl disable hysteria-panel
```

Удаление службы из автозагрузки и самой директории с кодом:
```bash
sudo rm /etc/systemd/system/hysteria-panel.service
sudo rm -rf /opt/hysteria-panel/
```

### 3. Финальная очистка
Обновление конфигураций системных служб, чтобы сервер забыл про удалённые файлы:
```bash
sudo systemctl daemon-reload
```

## 📄 Лицензия

MIT License. Делайте с кодом что хотите.

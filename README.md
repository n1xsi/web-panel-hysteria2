# ⚡ Hysteria2 Lightweight Web Panel

Простенькая и легковесная веб-панель управления пользователями для VPN-сервера на базе [Hysteria2](https://v2.hysteria.network/).


## 📌 Особенности
*   📝 **Генерация конфигураций:** Генерация ссылок и `.yaml`-конфигов (Clash/Mihomo/Clash Meta) на основе вашего шаблона (`config.yaml`).
*   🔗 **Генерация ссылок `hy2://`:** Напротив каждой ссылки есть кнопка для копирования, оснащённая fallback-скриптом на JavaScript, который позволяет копировать ссылки даже если панель работает по HTTP без SSL-сертификата.
*   🕒 **Отложенная перезагрузка:** Скрипт перезагружает службу `hysteria-server.service` с небольшой задержкой. Если вы сидите через свой же VPN, страница в браузере успеет обновиться до того, как VPN-соединение кратковременно разорвётся.
*   🔐 **Безопасность**: Доступ к панели защищён через Basic Auth (логин/пароль).

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

### 5. (Опционально) Настройка шаблона клиента
Вы можете отредактировать файл `client_template.yaml` под ваши нужды (добавить нужные правила маршрутизации / настройки обфускации).

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


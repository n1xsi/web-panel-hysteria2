from flask import Flask, render_template_string, request, redirect, url_for, Response
from flask_basicauth import BasicAuth
from ruamel.yaml import YAML
import subprocess
import threading
import secrets
import time


app = Flask(__name__)

# --- НАСТРОЙКИ ---
app.config['BASIC_AUTH_USERNAME'] = 'admin'
app.config['BASIC_AUTH_PASSWORD'] = 'admin'
app.config['BASIC_AUTH_FORCE'] = True

# --- ПУТИ ---
SERVER_CONFIG_PATH = '/etc/hysteria/config.yaml'
CLIENT_TEMPLATE_PATH = '/opt/hysteria-panel/client_template.yaml'
DOMAIN = 'example.com'

basic_auth = BasicAuth(app)

# Настройка YAML
yaml = YAML()
yaml.preserve_quotes = True
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.width = 4096


def load_server_config():
    with open(SERVER_CONFIG_PATH, 'r') as f:
        return yaml.load(f)


def save_server_config(data):
    with open(SERVER_CONFIG_PATH, 'w') as f:
        yaml.dump(data, f)


def restart_service_delayed():
    print("Ждём 2 секунды перед перезагрузкой...")
    time.sleep(2)
    try:
        print("Перезагрузка Hysteria...")
        subprocess.run(
            ['systemctl', 'restart', 'hysteria-server.service'], check=True)
    except Exception as e:
        print(f"Ошибка перезагрузки: {e}")


def restart_hysteria():
    thread = threading.Thread(target=restart_service_delayed)
    thread.start()


@app.route('/')
def index():
    config = load_server_config()
    users = config.get('auth', {}).get('userpass', {})

    user_list = []
    for user, password in users.items():
        link = f"hy2://{user}:{password}@{DOMAIN}:443?sni={DOMAIN}&alpn=h3&insecure=0&allowInsecure=0#{user}"
        user_list.append({
            'name': user,
            'password': password,
            'link': link
        })

    return render_template_string(HTML_TEMPLATE, users=user_list)


@app.route('/add', methods=['POST'])
def add_user():
    username = request.form.get('username')
    if username:
        username = username.strip()
        password = secrets.token_hex(16)

        config = load_server_config()
        if 'auth' not in config:
            config['auth'] = {}
        if 'userpass' not in config['auth']:
            config['auth']['userpass'] = {}

        config['auth']['userpass'][username] = password
        save_server_config(config)
        restart_hysteria()

    return redirect(url_for('index'))


@app.route('/delete/<username>')
def delete_user(username):
    config = load_server_config()
    if username in config.get('auth', {}).get('userpass', {}):
        del config['auth']['userpass'][username]
        save_server_config(config)
        restart_hysteria()
    return redirect(url_for('index'))


@app.route('/download/<username>')
def download_config(username):
    config = load_server_config()
    password = config.get('auth', {}).get('userpass', {}).get(username)
    if not password:
        return "User not found", 404

    with open(CLIENT_TEMPLATE_PATH, 'r') as f:
        template_content = f.read()

    auth_str = f"{username}:{password}"
    final_yaml = template_content.replace('{{ auth_str }}', auth_str)

    return Response(
        final_yaml,
        mimetype='application/x-yaml',
        headers={'Content-Disposition': f'attachment;filename={username}.yaml'}
    )


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hysteria2 Panel</title>
    <style>
        body { font-family: sans-serif; background: #121212; color: #e0e0e0; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .card { background: #1e1e1e; padding: 25px; border-radius: 12px; margin-bottom: 20px; }
        input[type="text"] { padding: 12px; width: 60%; }
        button { padding: 12px 20px; cursor: pointer; border: none; border-radius: 4px; }
        .btn-green { background: #00c853; color: white; }
        .btn-blue { background: #2979ff; color: white; text-decoration: none; padding: 8px 12px; border-radius: 4px; font-size: 14px; cursor: pointer; border: none;}
        .btn-red { background: #d50000; color: white; text-decoration: none; padding: 8px 12px; border-radius: 4px; font-size: 14px; margin-left: 5px;}
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        td { padding: 12px; border-bottom: 1px solid #333; }
        .code-box { background: #000; color: #76ff03; padding: 4px; font-family: monospace; }
    </style>
    <script>
        function copyLink(text, btnElement) {
            // Создаём скрытое поле
            const textArea = document.createElement("textarea");
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            
            try {
                // Пытаемся скопировать
                var successful = document.execCommand('copy');
                if (successful) {
                    const originalText = btnElement.innerText;
                    btnElement.innerText = "Скопировано!";
                    setTimeout(() => btnElement.innerText = originalText, 2000);
                } else {
                    throw new Error("Copy failed");
                }
            } catch (err) {
                // ЕСЛИ НЕ ПОЛУЧИЛОСЬ (браузер заблокировал) - Показываем окно
                prompt("Браузер запретил авто-копирование. Нажмите Ctrl+C, чтобы скопировать:", text);
            }
            document.body.removeChild(textArea);
        }
    </script>
</head>
<body>
    <div class="container">
        <h1>⚡ Hysteria2 Panel</h1>
        
        <div class="card">
            <h3>Добавить пользователя</h3>
            <form action="/add" method="POST">
                <input type="text" name="username" placeholder="Имя (английские буквы)" required>
                <button type="submit" class="btn-green">Создать + Перезагрузить</button>
            </form>
            <p style="font-size: 12px; color: #888;">Сервер перезагрузится через 2 секунды после нажатия.</p>
        </div>

        <div class="card">
            <h3>Пользователи</h3>
            <table>
                {% for u in users %}
                <tr>
                    <td><b>{{ u.name }}</b></td>
                    <td><span class="code-box">{{ u.password }}</span></td>
                    <td>
                        <button class="btn-blue" onclick="copyLink('{{ u.link }}', this)">Ссылка</button>
                        <a href="/download/{{ u.name }}" class="btn-blue">.yaml</a>
                        <a href="/delete/{{ u.name }}" class="btn-red" onclick="return confirm('Удалить?')">X</a>
                    </td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </div>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

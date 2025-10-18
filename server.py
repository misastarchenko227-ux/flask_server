import sqlite3
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

print("путь к бд", os.path.abspath("users.db"))

# ✅ Создание базы данных и таблицы (если нет)
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    return "Сервер работает! ✅"

# ✅ Регистрация
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')

    if not email or not password or not name:
        return jsonify({
            'message': 'Ошибка: Email, пароль и имя обязательны',
            'error': 'missing_fields',
            'email': email or "",
            'success': False
        }), 400

    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (email, password, name) VALUES (?, ?, ?)", (email, password, name))
        conn.commit()
        conn.close()
        return jsonify({
            'message': 'Регистрация успешна',
            'error': '',
            'email': email,
            'success': True
        }), 201
    except sqlite3.IntegrityError:
        return jsonify({
            'message': 'Ошибка: пользователь уже существует',
            'error': 'user_exists',
            'email': email,
            'success': False
        }), 409

# ✅ Логин
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({
            'message': 'Ошибка: Email и пароль обязательны',
            'error': 'missing_fields',
            'email': email or "",
            'success': False
        }), 400

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT name FROM users WHERE email = ? AND password = ?", (email, password))
    result = c.fetchone()
    conn.close()

    if result:
        return jsonify({
            'message': f'Добро пожаловать, {result[0]}!',
            'error': '',
            'email': email,
            'success': True
        }), 200
    else:
        return jsonify({
            'message': 'Неверный email или пароль',
            'error': 'invalid_credentials',
            'email': email,
            'success': False
        }), 401

# ✅ Проверка имени
@app.route('/user', methods=['POST'])
def user():
    data = request.json
    name = data.get('name')

    if not name:
        return jsonify({
            'message': 'Имя не указано',
            'error': 'missing_name',
            'email': "",
            'success': False
        }), 400

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT email FROM users WHERE name = ?", (name,))
    result = c.fetchone()
    conn.close()

    if result:
        return jsonify({
            'message': 'Пользователь найден',
            'error': '',
            'email': result[0],
            'success': True
        }), 200
    else:
        return jsonify({
            'message': 'Пользователь не найден',
            'error': 'not_found',
            'email': "",
            'success': False
        }), 404

# ✅ Список пользователей
@app.route('/users', methods=['GET'])
def list_users():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT email FROM users")
    users = [row[0] for row in c.fetchall()]
    conn.close()
    return jsonify({
        'message': 'Список пользователей',
        'error': '',
        'email': "",
        'success': True,
        'users': users
    })

if __name__ == '__main__':
     # 🔒 добавляем сертификаты
  port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)

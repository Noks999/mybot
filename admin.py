from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user
import aiosqlite
import asyncio
from datetime import datetime, timedelta
import random
import string

app = Flask(__name__)
app.secret_key = 'exploit-xiters-2024'

BOT_TOKEN = "8544716257:AAHF_UBpvTs7IMB7aFm69-ycdYF7_qemEOo"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

ADMIN_USER = 'admin'
ADMIN_PASS = 'admin123'

class User:
    def __init__(self, id):
        self.id = id
    def is_authenticated(self):
        return True
    def is_active(self):
        return True
    def is_anonymous(self):
        return False
    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# Отправка сообщений через Telegram
def send_telegram(user_id, text):
    try:
        import requests
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": user_id, "text": text}, timeout=5)
    except:
        pass

@app.route('/')
@login_required
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Exploit Xiters - Admin</title>
        <meta charset="utf-8">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: Arial; background: #1a1a2e; color: white; }
            .header { background: #0f3460; padding: 20px; text-align: center; }
            .header h1 { color: #e94560; }
            .container { max-width: 1200px; margin: 20px auto; padding: 20px; }
            .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }
            .stat-card { background: #0f3460; padding: 20px; border-radius: 10px; text-align: center; }
            .stat-card h3 { color: #e94560; }
            .stat-card .value { font-size: 32px; margin-top: 10px; }
            .section { background: #0f3460; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
            .section h2 { color: #e94560; margin-bottom: 15px; }
            table { width: 100%; border-collapse: collapse; }
            th { background: #e94560; padding: 10px; }
            td { padding: 10px; border-bottom: 1px solid #16213e; }
            .btn { padding: 5px 15px; border: none; border-radius: 3px; cursor: pointer; margin: 2px; }
            .btn-approve { background: #00b894; color: white; }
            .btn-cancel { background: #e94560; color: white; }
            .alert { padding: 15px; border-radius: 5px; margin: 10px 0; display: none; }
            .alert-success { background: #00b894; }
            .alert-error { background: #e94560; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>💎 Exploit Xiters - Панель управления</h1>
            <a href="/logout" style="position:absolute;right:20px;top:20px;color:white;background:#e94560;padding:10px 20px;text-decoration:none;border-radius:5px;">🚪 Выход</a>
        </div>
        <div class="container">
            <div class="alert" id="alert"></div>
            <div class="stats" id="stats"></div>
            <div class="section">
                <h2>📦 Заказы <button onclick="loadData()" style="float:right;background:#e94560;color:white;border:none;padding:5px 15px;border-radius:3px;cursor:pointer;">🔄 Обновить</button></h2>
                <table id="ordersTable">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>User ID</th>
                            <th>Товар</th>
                            <th>Сумма</th>
                            <th>Дни</th>
                            <th>Статус</th>
                            <th>Дата</th>
                            <th>Действия</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>
        <script>
            async function loadData() {
                const res = await fetch('/api/stats');
                const data = await res.json();
                document.getElementById('stats').innerHTML = `
                    <div class="stat-card"><h3>👥 Пользователи</h3><div class="value">${data.users}</div></div>
                    <div class="stat-card"><h3>📦 Заказы</h3><div class="value">${data.orders}</div></div>
                    <div class="stat-card"><h3>✅ Выполнено</h3><div class="value">${data.completed}</div></div>
                    <div class="stat-card"><h3>💰 Доход</h3><div class="value">${data.revenue} ₽</div></div>
                `;
                
                const ordersRes = await fetch('/api/orders');
                const orders = await ordersRes.json();
                const tbody = document.querySelector('#ordersTable tbody');
                tbody.innerHTML = orders.map(o => `
                    <tr>
                        <td>#${o.id}</td>
                        <td>${o.user_id}</td>
                        <td>${o.product_name}</td>
                        <td>${o.amount}₽</td>
                        <td>${o.days}д</td>
                        <td class="status-${o.status}">${o.status === 'pending' ? '⏳ Ожидает' : '✅ Выполнен'}</td>
                        <td>${o.created_at ? o.created_at.slice(0,10) : '-'}</td>
                        <td>
                            ${o.status === 'pending' ? 
                                `<button class="btn btn-approve" onclick="approve(${o.id})">✅</button>
                                 <button class="btn btn-cancel" onclick="cancel(${o.id})">❌</button>` 
                                : '✅'}
                        </td>
                    </tr>
                `).join('');
            }
            
            function showAlert(msg, type) {
                const alert = document.getElementById('alert');
                alert.className = 'alert alert-' + type;
                alert.textContent = msg;
                alert.style.display = 'block';
                setTimeout(() => alert.style.display = 'none', 3000);
            }
            
            async function approve(id) {
                if(!confirm('Подтвердить заказ #' + id + '?')) return;
                const res = await fetch('/api/approve/' + id, {method:'POST'});
                const data = await res.json();
                if(data.success) {
                    showAlert('✅ Заказ подтвержден! Ключ: ' + data.key, 'success');
                } else {
                    showAlert('❌ Ошибка: ' + (data.error || 'Неизвестно'), 'error');
                }
                loadData();
            }
            
            async function cancel(id) {
                if(!confirm('Отменить заказ #' + id + '?')) return;
                await fetch('/api/cancel/' + id, {method:'POST'});
                showAlert('❌ Заказ отменен', 'error');
                loadData();
            }
            
            loadData();
            setInterval(loadData, 10000);
        </script>
    </body>
    </html>
    '''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USER and password == ADMIN_PASS:
            login_user(User(1))
            return redirect(url_for('index'))
        
        return '<h2 style="color:red;text-align:center;">Неверный пароль!</h2><a href="/login">Назад</a>'
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Exploit Xiters - Вход</title>
        <meta charset="utf-8">
        <style>
            body { background: #1a1a2e; display: flex; justify-content: center; align-items: center; height: 100vh; font-family: Arial; }
            .box { background: #0f3460; padding: 40px; border-radius: 15px; width: 350px; color: white; }
            h1 { color: #e94560; text-align: center; margin-bottom: 30px; }
            input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #e94560; border-radius: 5px; background: #1a1a2e; color: white; }
            button { width: 100%; padding: 12px; background: #e94560; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; margin-top: 15px; }
        </style>
    </head>
    <body>
        <div class="box">
            <h1>🔐 Exploit Xiters</h1>
            <form method="POST">
                <input type="text" name="username" placeholder="Логин" required>
                <input type="password" name="password" placeholder="Пароль" required>
                <button type="submit">ВОЙТИ</button>
            </form>
        </div>
    </body>
    </html>
    '''

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/api/stats')
@login_required
def stats():
    async def get():
        async with aiosqlite.connect('exploit.db') as db:
            c = await db.execute('SELECT COUNT(*) FROM users')
            users = (await c.fetchone())[0]
            c = await db.execute('SELECT COUNT(*) FROM orders')
            orders = (await c.fetchone())[0]
            c = await db.execute("SELECT COUNT(*) FROM orders WHERE status='completed'")
            completed = (await c.fetchone())[0]
            c = await db.execute("SELECT COALESCE(SUM(amount),0) FROM orders WHERE status='completed'")
            revenue = (await c.fetchone())[0]
            return {'users': users, 'orders': orders, 'completed': completed, 'revenue': revenue}
    loop = asyncio.new_event_loop()
    return jsonify(loop.run_until_complete(get()))

@app.route('/api/orders')
@login_required
def orders():
    async def get():
        async with aiosqlite.connect('exploit.db') as db:
            db.row_factory = aiosqlite.Row
            c = await db.execute('SELECT * FROM orders ORDER BY created_at DESC LIMIT 50')
            return [dict(r) for r in await c.fetchall()]
    loop = asyncio.new_event_loop()
    return jsonify(loop.run_until_complete(get()))

@app.route('/api/approve/<int:order_id>', methods=['POST'])
@login_required
def approve(order_id):
    async def do():
        key = f"EX-{random.randint(1000,9999)}-{''.join(random.choices(string.ascii_uppercase, k=4))}"
        async with aiosqlite.connect('exploit.db') as db:
            db.row_factory = aiosqlite.Row
            c = await db.execute('SELECT * FROM orders WHERE id=?', (order_id,))
            order = await c.fetchone()
            if order:
                await db.execute("UPDATE orders SET status='completed' WHERE id=?", (order_id,))
                exp = (datetime.now() + timedelta(days=order['days'])).isoformat()
                await db.execute(
                    "INSERT INTO keys (key, product_type, product_name, days, is_used, used_by, order_id, created_at, expires_at) VALUES (?, ?, ?, ?, 1, ?, ?, ?, ?)",
                    (key, order['product_type'], order['product_name'], order['days'], order['user_id'], order_id, datetime.now().isoformat(), exp))
                await db.commit()
                
                # Отправляем пользователю
                send_telegram(order['user_id'],
                    f"✅ ЗАКАЗ №{order_id} ПОДТВЕРЖДЕН!\n\n"
                    f"📦 {order['product_name']}\n"
                    f"🔑 {key}\n"
                    f"⏱ {order['days']} дн.\n\n"
                    f"Спасибо за покупку!")
                
                return {'success': True, 'key': key}
        return {'success': False, 'error': 'Заказ не найден'}
    loop = asyncio.new_event_loop()
    return jsonify(loop.run_until_complete(do()))

@app.route('/api/cancel/<int:order_id>', methods=['POST'])
@login_required
def cancel(order_id):
    async def do():
        async with aiosqlite.connect('exploit.db') as db:
            await db.execute("UPDATE orders SET status='cancelled' WHERE id=?", (order_id,))
            await db.commit()
        return {'success': True}
    loop = asyncio.new_event_loop()
    return jsonify(loop.run_until_complete(do()))

if __name__ == '__main__':
    print("=" * 50)
    print("🌐 Exploit Xiters Admin Panel")
    print("📍 http://localhost:5000")
    print("👤 admin")
    print("🔑 admin123")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=False)